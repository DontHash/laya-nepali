"""LLM-assisted candidate generation (P1).

Pipeline: ``templates.build_plan`` -> Gemini Flash-Lite writes one natural
customer message per (family, language, business) -> validate (script, PII,
length) -> derive soft gold from the family -> append a schema-valid candidate
row to ``data/generated/``.

Rows are candidates only: ``provenance.reviewed_by`` stays null until the review
pass (``review.py``) accepts or edits them into ``data/reviewed/``.

The Gemini client is stdlib-only (urllib) with key rotation and paced retries;
tests inject a fake generator, so CI stays offline.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Protocol, Sequence

from .normalize import normalize_text
from .schema import SchemaError, validate_case
from .spelling import apply_spelling_variant
from .templates import TRAINING_BUSINESSES, GenerationTask, build_case, build_plan
from .transliterate import DEVANAGARI_RE
from .validate import scan_pii

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO_ROOT / "data" / "generated" / "ne-candidates.jsonl"
DEFAULT_MODEL = "gemini-3.5-flash-lite"
DEFAULT_SEED = 20260925
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
KEY_ENV_NAMES = ("GEMINI_API_KEY", "GEMINI_API_KEY_ALT2", "GEMINI_API_KEY_ALT3", "GEMINI_API_KEY_ALT4")
MAX_MESSAGE_CHARS = 200
RETRYABLE_STATUS = {429, 500, 502, 503, 504}
MIXED_SCRIPT_TOKEN = re.compile(r"[A-Za-z][\u0900-\u097F]|[\u0900-\u097F][A-Za-z]")
DEDUP_TOKEN_RE = re.compile(r"[\u0900-\u097F]+|[a-z]+|\d+")
DUPLICATE_JACCARD = 0.9

JUDGE_PROMPT = (
    "You check one Nepali customer message against the intent it was written for.\n"
    "Intent: {instruction}\n"
    "Message: {message}\n"
    "Does the message express exactly this intent and nothing else? "
    "Answer with one word, YES or NO, followed by a short reason."
)


class GenerationError(RuntimeError):
    """A message could not be generated (configuration, quota or provider error)."""


class TextGenerator(Protocol):
    def generate(self, prompt: str) -> str:  # pragma: no cover - protocol
        ...


class _Retryable(RuntimeError):
    pass


def load_env_file(path: Path) -> dict[str, str]:
    """Read ``KEY=VALUE`` lines; existing environment variables are not overridden."""
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, _, value = line.partition("=")
        name, value = name.strip(), value.strip().strip('"').strip("'")
        if not name:
            continue
        values[name] = value
        os.environ.setdefault(name, value)
    return values


def gemini_keys() -> list[str]:
    return [os.environ.get(name, "").strip() for name in KEY_ENV_NAMES if os.environ.get(name, "").strip()]


class GeminiGenerator:
    """Minimal REST client for ``generativelanguage.googleapis.com``."""

    def __init__(
        self,
        keys: Sequence[str],
        *,
        model: str = DEFAULT_MODEL,
        timeout: float = 60.0,
        retries: int = 3,
        temperature: float = 1.0,
        max_output_tokens: int = 256,
        backoff_seconds: float = 5.0,
    ) -> None:
        if not keys:
            raise GenerationError("no Gemini API keys found; copy .env.example to .env and fill the keys")
        self._keys = list(keys)
        self._model = model
        self._timeout = timeout
        self._retries = max(1, retries)
        self._temperature = temperature
        self._max_output_tokens = max_output_tokens
        self._backoff_seconds = backoff_seconds
        self._cursor = 0
        self._thinking_level = "minimal" if model.startswith("gemini-3") else None

    def generate(self, prompt: str) -> str:
        max_attempts = self._retries * len(self._keys)
        last_error: Exception | None = None
        for attempt in range(max_attempts):
            key = self._keys[self._cursor % len(self._keys)]
            self._cursor += 1
            try:
                return self._extract_text(self._call(prompt, key))
            except _Retryable as exc:
                last_error = exc
                time.sleep(min(30.0, self._backoff_seconds * (2 ** (attempt // len(self._keys)))))
        raise GenerationError(f"Gemini request failed after {max_attempts} attempts: {last_error}")

    def _call(self, prompt: str, key: str) -> dict:
        generation_config: dict = {
            "temperature": self._temperature,
            "maxOutputTokens": self._max_output_tokens,
        }
        if self._thinking_level:
            generation_config["thinkingConfig"] = {"thinkingLevel": self._thinking_level}
        payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": generation_config}
        request = urllib.request.Request(
            GEMINI_ENDPOINT.format(model=self._model) + f"?key={key}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in RETRYABLE_STATUS:
                raise _Retryable(f"HTTP {exc.code}") from exc
            raise GenerationError(f"Gemini HTTP {exc.code}: {exc.reason}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise _Retryable(str(exc)) from exc

    @staticmethod
    def _extract_text(data: dict) -> str:
        feedback = data.get("promptFeedback") or {}
        if feedback.get("blockReason"):
            raise GenerationError(f"Gemini blocked the prompt: {feedback['blockReason']}")
        candidates = data.get("candidates") or []
        if not candidates:
            raise GenerationError("Gemini returned no candidates")
        parts = (candidates[0].get("content") or {}).get("parts") or []
        text = " ".join(str(part.get("text", "")) for part in parts).strip()
        if not text:
            raise GenerationError("Gemini returned an empty message")
        return text


def normalize_message(raw: str) -> str:
    return normalize_text(raw)


def _stray_script_letter(message: str) -> str | None:
    """First non-ASCII, non-Devanagari letter (catches Cyrillic lookalikes)."""
    for char in message:
        if char.isalpha() and not char.isascii() and not DEVANAGARI_RE.match(char):
            return char
    return None


def validate_message(message: str, language: str, business_name: str | None = None) -> list[str]:
    reasons: list[str] = []
    if not message:
        reasons.append("empty")
    if len(message) > MAX_MESSAGE_CHARS:
        reasons.append(f"too long ({len(message)} chars)")
    pii = scan_pii(message)
    if pii:
        reasons.append("pii:" + ",".join(pii))
    if MIXED_SCRIPT_TOKEN.search(message):
        reasons.append("mixed-script token")
    stray = _stray_script_letter(message)
    if stray is not None:
        reasons.append(f"unexpected script character {stray!r}")
    if business_name:
        lowered = message.lower()
        for token in business_name.lower().split():
            if len(token) > 3 and token in lowered:
                reasons.append("mentions the restaurant name")
                break
    has_devanagari = bool(DEVANAGARI_RE.search(message))
    latin_letters = sum(1 for char in message if char.isascii() and char.isalpha())
    if language == "ne":
        if not has_devanagari:
            reasons.append("expected Devanagari script")
    else:
        if has_devanagari:
            reasons.append("expected Latin script")
        if latin_letters < 3:
            reasons.append("too little Latin text")
    return reasons


@dataclass(frozen=True)
class JudgeVerdict:
    expresses: bool
    reason: str


def judge_message(judge: TextGenerator, instruction: str, message: str) -> JudgeVerdict:
    raw = judge.generate(JUDGE_PROMPT.format(instruction=instruction, message=message))
    parts = raw.strip().split(maxsplit=1)
    first = parts[0].strip(".,!:").upper() if parts else ""
    reason = parts[1].strip() if len(parts) > 1 else ""
    return JudgeVerdict(expresses=first in ("YES", "Y"), reason=reason or raw.strip())


def _normalized_key(text: str) -> str:
    return " ".join(text.lower().split())


def _token_set(text: str) -> frozenset[str]:
    return frozenset(DEDUP_TOKEN_RE.findall(text.lower()))


def _is_duplicate(text: str, seen_keys: set[str], seen_tokens: list[frozenset[str]]) -> bool:
    if _normalized_key(text) in seen_keys:
        return True
    tokens = _token_set(text)
    if not tokens:
        return False
    for other in seen_tokens:
        union = tokens | other
        if union and len(tokens & other) / len(union) >= DUPLICATE_JACCARD:
            return True
    return False


@dataclass
class GenerationReport:
    planned: int
    output: Path
    accepted: int = 0
    variants: int = 0
    skipped: int = 0
    rejected: list[tuple[str, list[str]]] = field(default_factory=list)
    failed: list[tuple[str, str]] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"planned {self.planned} | accepted {self.accepted} | variants {self.variants} | "
            f"skipped {self.skipped} | rejected {len(self.rejected)} | failed {len(self.failed)}"
        )


def _prime_from_existing(path: Path, seen: dict, report: GenerationReport) -> set[str]:
    existing_ids: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        existing_ids.add(str(row.get("id", "")))
        state = row.get("state", {})
        if isinstance(state, str):
            state = json.loads(state)
        message = str((state or {}).get("customer_message", ""))
        family = str((row.get("provenance") or {}).get("family", ""))
        if message and family:
            keys, tokens = seen.setdefault(family, (set(), []))
            keys.add(_normalized_key(message))
            tokens.append(_token_set(message))
    report.skipped = 0
    return existing_ids


def generate_candidates(
    tasks: Sequence[GenerationTask],
    generator: TextGenerator,
    *,
    generator_name: str,
    out_path: Path,
    seed: int = DEFAULT_SEED,
    delay_ms: int = 0,
    progress_every: int = 0,
    judge: TextGenerator | None = None,
    spelling_share: float = 0.0,
    resume: bool = False,
    forbidden_texts: set[str] | None = None,
) -> GenerationReport:
    report = GenerationReport(planned=len(tasks), output=out_path)
    rng = random.Random(seed)
    seen: dict[str, tuple[set[str], list[frozenset[str]]]] = {}
    calls = 0

    def call(client: TextGenerator, prompt: str) -> str:
        nonlocal calls
        if delay_ms and calls:
            time.sleep(delay_ms / 1000)
        calls += 1
        return client.generate(prompt)

    existing_ids: set[str] = set()
    mode = "w"
    if resume and out_path.exists():
        existing_ids = _prime_from_existing(out_path, seen, report)
        mode = "a"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open(mode, encoding="utf-8") as sink:
        for index, task in enumerate(tasks):
            if task.id in existing_ids:
                report.skipped += 1
                continue
            try:
                raw = call(generator, task.prompt)
            except GenerationError as exc:
                report.failed.append((task.id, str(exc)))
                continue
            message = normalize_message(raw)
            reasons = validate_message(message, task.language, task.business.name)
            if not reasons and forbidden_texts and normalize_text(message).lower() in forbidden_texts:
                reasons = ["benchmark collision"]
            if reasons:
                report.rejected.append((task.id, reasons))
                continue
            if judge is not None:
                try:
                    verdict = judge_message(judge, task.family.instruction, message)
                except GenerationError as exc:
                    report.failed.append((task.id, f"judge: {exc}"))
                    continue
                if not verdict.expresses:
                    report.rejected.append((task.id, [f"judge: {verdict.reason or 'not this intent'}"]))
                    continue
            seen_keys, seen_tokens = seen.setdefault(task.family.id, (set(), []))
            if _is_duplicate(message, seen_keys, seen_tokens):
                report.rejected.append((task.id, ["duplicate"]))
                continue
            seen_keys.add(_normalized_key(message))
            seen_tokens.append(_token_set(message))

            case = build_case(task, message, rng, generator=generator_name)
            try:
                validate_case(case)
            except SchemaError as exc:
                report.rejected.append((task.id, [f"schema: {exc}"]))
                continue
            sink.write(json.dumps(case.to_row(), ensure_ascii=False) + "\n")
            report.accepted += 1

            if spelling_share and rng.random() < spelling_share:
                variant_text = apply_spelling_variant(message, rng)
                if variant_text:
                    variant_case = build_case(task, variant_text, rng, generator=generator_name)
                    variant_case.id = f"{task.id}-v1"
                    variant_case.provenance["augmentation"] = "spelling-v1"
                    variant_case.provenance["variant_of"] = task.id
                    try:
                        validate_case(variant_case)
                    except SchemaError:
                        pass
                    else:
                        sink.write(json.dumps(variant_case.to_row(), ensure_ascii=False) + "\n")
                        report.variants += 1

            if progress_every and (index + 1) % progress_every == 0:
                print(
                    f"  {index + 1}/{len(tasks)} processed "
                    f"({report.accepted} accepted, {report.variants} variants)"
                )
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Nepali typed-decision candidates with Gemini.")
    parser.add_argument("--cases", type=int, default=0, help="max candidates to plan (0 = all)")
    parser.add_argument("--kind-cases", type=int, default=100, help="cases per command-kind family")
    parser.add_argument("--safety-cases", type=int, default=40, help="cases per safety/abstain family")
    parser.add_argument("--businesses", type=int, default=0, help="max training businesses (0 = all)")
    parser.add_argument("--languages", default="ne", help="comma-separated language mix")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--model", default=None, help=f"Gemini model (default {DEFAULT_MODEL} or $GEMINI_MODEL)")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--delay-ms", type=int, default=4500, help="pause between API calls for the free tier")
    parser.add_argument("--retries", type=int, default=3, help="attempts per API key")
    parser.add_argument("--no-judge", action="store_true", help="skip the LLM judge pass")
    parser.add_argument("--spelling-share", type=float, default=0.15, help="share of rows that also emit a spelling variant")
    parser.add_argument("--resume", action="store_true", help="skip tasks already present in --out and append")
    parser.add_argument("--dry-run", action="store_true", help="print the plan and sample prompts, no API calls")
    args = parser.parse_args(argv)

    languages = [language.strip() for language in args.languages.split(",") if language.strip()]
    businesses = TRAINING_BUSINESSES[: args.businesses] if args.businesses else TRAINING_BUSINESSES
    tasks = build_plan(
        businesses=businesses,
        languages=languages,
        kind_cases=max(0, args.kind_cases),
        safety_cases=max(0, args.safety_cases),
        limit=args.cases or None,
    )

    if args.dry_run:
        families = {task.family.id for task in tasks}
        print(
            f"plan: {len(tasks)} tasks | {len(families)} families | {len(languages)} languages | "
            f"{len(businesses)} businesses | judge={'off' if args.no_judge else 'on'} | "
            f"spelling share {args.spelling_share}"
        )
        for task in tasks[:3]:
            print(f"\n--- {task.id} | {task.family.id} | {task.language} | {task.business.id} ---")
            print(task.prompt)
        return 0

    load_env_file(REPO_ROOT / ".env")
    model = args.model or os.environ.get("GEMINI_MODEL") or DEFAULT_MODEL
    model_name = model if model.startswith("gemini-") else f"gemini-{model}"
    generator = GeminiGenerator(gemini_keys(), model=model, retries=args.retries)
    judge = None
    if not args.no_judge:
        judge = GeminiGenerator(gemini_keys(), model=model, retries=args.retries, temperature=0.0, max_output_tokens=128)
    from .export import benchmark_texts

    report = generate_candidates(
        tasks,
        generator,
        generator_name=f"{model_name}@{date.today().isoformat()}",
        out_path=args.out,
        seed=args.seed,
        delay_ms=args.delay_ms,
        progress_every=10,
        judge=judge,
        spelling_share=max(0.0, min(1.0, args.spelling_share)),
        resume=args.resume,
        forbidden_texts=benchmark_texts(),
    )
    print(report.summary())
    for task_id, reasons in report.rejected[:10]:
        print(f"  reject {task_id}: {', '.join(reasons)}")
    for task_id, error in report.failed[:10]:
        print(f"  fail   {task_id}: {error}")
    if report.accepted:
        print(f"wrote {report.output}")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
