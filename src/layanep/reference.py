"""Register statistics and rules distilled from Nepali reference sources (P1b).

Reference-only sources (NepTrans transcripts, LINCE, tweets, chat corpora) are
read for statistics and patterns; no text from them enters the dataset. The
computed profile validates the hand-curated ``REGISTER_RULES`` that the
generator prompt and the LLM judge consume, and ``render_register_markdown``
writes ``docs/register.md``.

Usage::

    python -m layanep.reference \
        --source "reviewed batch 1=data/reviewed/ne-decisions-v1.jsonl" \
        --source "NepTrans podcasts=D:/Code/NepTrans/Transcript" \
        --out docs/register.md
"""

from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .validate import load_rows

TOKEN_RE = re.compile(r"[\u0900-\u097F]+|[A-Za-z]+|\d+")
DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")
LATIN_RE = re.compile(r"[A-Za-z]")

PARTICLES = ("नि", "है", "त", "ला", "हजुर", "दाइ", "दिदी")

REGISTER_RULES: tuple[str, ...] = (
    "Keep messages short: reviewed commands sit at p50 6 words / p90 10; conversational speech runs p50 12 / p90 18.",
    "Write the way people type on WhatsApp, not formal prose.",
    "Use spoken particles where they fit: नि, है, त, ला, and दाइ/दिदी/हजुर for people (reviewed commands use them ~7 per 100 words).",
    "Use English loanwords only where people borrow them (order, delivery, cart, rate): "
    "conversational podcasts run ~17% Latin tokens, but short command messages are often pure Devanagari.",
    "Questions use कति/के/कहाँ/कहिले with verb-final phrasing.",
    "Devanagari digits (१२३) are acceptable for quantities.",
    "No emojis, no URLs, no names, addresses or phone numbers.",
)


@dataclass(frozen=True)
class TextProfile:
    label: str
    messages: int
    words: int
    words_p50: float
    words_p90: float
    latin_token_share: float
    particles_per_100_words: float
    question_share: float
    devanagari_messages: int


def _tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(text)


def _percentile(values: Sequence[float], percent: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(percent / 100 * len(ordered)) - 1))
    return float(ordered[index])


def profile_texts(texts: Sequence[str], *, label: str = "texts", devanagari_only: bool = False) -> TextProfile:
    if devanagari_only:
        texts = [text for text in texts if DEVANAGARI_RE.search(text)]
    texts = [text for text in texts if text and text.strip()]
    token_lists = [_tokens(text) for text in texts]
    total_tokens = sum(len(tokens) for tokens in token_lists)
    latin_tokens = sum(1 for tokens in token_lists for token in tokens if LATIN_RE.search(token))
    particle_hits = sum(
        1 for tokens in token_lists for token in tokens if token in PARTICLES
    )
    question_messages = sum(1 for text in texts if "?" in text)
    devanagari_messages = sum(1 for text in texts if DEVANAGARI_RE.search(text))
    word_counts = [float(len(tokens)) for tokens in token_lists]
    return TextProfile(
        label=label,
        messages=len(texts),
        words=total_tokens,
        words_p50=round(_percentile(word_counts, 50), 1),
        words_p90=round(_percentile(word_counts, 90), 1),
        latin_token_share=round(latin_tokens / total_tokens, 3) if total_tokens else 0.0,
        particles_per_100_words=round(particle_hits / total_tokens * 100, 1) if total_tokens else 0.0,
        question_share=round(question_messages / len(texts), 3) if texts else 0.0,
        devanagari_messages=devanagari_messages,
    )


def messages_from_rows(rows: Sequence[dict]) -> list[str]:
    messages: list[str] = []
    for row in rows:
        state = row.get("state", {})
        if isinstance(state, str):
            try:
                state = json.loads(state)
            except json.JSONDecodeError:
                continue
        if isinstance(state, dict) and state.get("customer_message"):
            messages.append(str(state["customer_message"]))
    return messages


def load_source(spec: str) -> tuple[str, list[str]]:
    """Load one reference source: ``label=PATH`` where PATH is JSONL or a .txt directory."""
    label, separator, raw_path = spec.partition("=")
    path = Path(raw_path if separator else spec)
    label = label.strip() if separator else path.name
    if path.is_dir():
        lines: list[str] = []
        for child in sorted(path.rglob("*.txt")):
            lines.extend(child.read_text(encoding="utf-8", errors="ignore").splitlines())
        return label, [line.strip() for line in lines if line.strip()]
    if path.suffix in {".jsonl", ".json"}:
        return label, messages_from_rows(load_rows(path))
    raise ValueError(f"unsupported reference source {path} (use JSONL or a .txt directory)")


def render_register_markdown(profiles: Sequence[TextProfile]) -> str:
    lines = [
        "# Nepali register profile",
        "",
        "Computed from reference sources for the generator prompt and the LLM judge.",
        "Reference text is never stored or shipped; only these statistics and the rules below.",
        "",
        "| source | messages | words | p50 words | p90 words | Latin token share | particles /100 words | ends with ? | Devanagari |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for profile in profiles:
        lines.append(
            f"| {profile.label} | {profile.messages} | {profile.words} | {profile.words_p50} | "
            f"{profile.words_p90} | {profile.latin_token_share:.3f} | {profile.particles_per_100_words} | "
            f"{profile.question_share:.3f} | {profile.devanagari_messages} |"
        )
    lines.extend(["", "## Register rules (generator prompt + judge rubric)", ""])
    lines.extend(f"{index}. {rule}" for index, rule in enumerate(REGISTER_RULES, start=1))
    lines.extend(
        [
            "",
            "## Method",
            "",
            "- Generated by `python -m layanep.reference --source <label=path> ... --out docs/register.md`.",
            "- Lanes per `docs/provenance.md`: NepTrans/LINCE/tweets are reference-only; "
            "the reviewed batch is our own CC BY 4.0 data.",
            "- Message-length guidance leans on the reviewed batch; particle and code-switch "
            "densities lean on the conversational references.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Profile Nepali register from reference sources.")
    parser.add_argument("--source", action="append", required=True, help="label=PATH (JSONL or .txt directory)")
    parser.add_argument("--devanagari-only", action="store_true", help="ignore non-Devanagari lines/messages")
    parser.add_argument("--out", type=Path, default=None, help="write markdown here")
    args = parser.parse_args(argv)

    profiles = []
    for spec in args.source:
        label, texts = load_source(spec)
        profiles.append(profile_texts(texts, label=label, devanagari_only=args.devanagari_only))
        print(f"{label}: {profiles[-1].messages} messages, {profiles[-1].words} tokens")

    markdown = render_register_markdown(profiles)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(markdown, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
