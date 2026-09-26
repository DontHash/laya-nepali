"""Import an external message bank (``{message, family}``) into schema cases.

Writing LLMs should never touch ids, state, gold labels or probabilities: this
module derives all of them through ``templates.build_case`` from the family id,
validates every message with the same gate the generator uses, and drops rows
that collide with the frozen benchmark or duplicate the existing corpus.
"""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Sequence

from .export import DEFAULT_BENCHMARK_PATHS, benchmark_texts
from .generate import validate_message
from .normalize import normalize_text
from .templates import (
    FAMILY_BY_ID,
    TRAINING_BUSINESSES,
    GenerationTask,
    build_case,
    build_prompt,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO_ROOT / "data" / "generated" / "ne-bank.jsonl"
DEFAULT_CORPUS = (
    REPO_ROOT / "data" / "reviewed" / "ne-decisions-v1.jsonl",
    REPO_ROOT / "data" / "generated" / "ne-candidates-v2.jsonl",
)
DEFAULT_ID_PREFIX = "ne-bank"
GENERATOR = "external-llm:bank"
MAX_WORDS = 15


@dataclass
class ImportReport:
    total: int = 0
    imported: int = 0
    skipped_lines: int = 0
    skipped: dict[str, int] = field(default_factory=dict)
    failures: list[tuple[int, str]] = field(default_factory=list)

    def note(self, reason: str) -> None:
        self.skipped[reason] = self.skipped.get(reason, 0) + 1

    def summary(self) -> str:
        parts = " | ".join(f"{reason} {count}" for reason, count in sorted(self.skipped.items()))
        return f"total {self.total} | imported {self.imported}" + (f" | skipped: {parts}" if parts else "")


def load_corpus_messages(paths: Sequence[Path]) -> set[str]:
    messages: set[str] = set()
    for path in paths:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            message = json.loads(row["state"]).get("customer_message", "")
            messages.add(normalize_text(str(message)).lower())
    return messages


def import_entries(
    entries: Sequence[Mapping[str, object]],
    *,
    forbidden: set[str] | None = None,
    existing: set[str] | None = None,
    id_prefix: str = DEFAULT_ID_PREFIX,
    seed: int = 0,
    generator: str = GENERATOR,
) -> tuple[list[dict], ImportReport]:
    report = ImportReport(total=len(entries))
    forbidden = forbidden or set()
    existing = existing or set()
    seen: set[str] = set()
    rows: list[dict] = []
    for index, entry in enumerate(entries, start=1):
        message = entry.get("message")
        family_id = entry.get("family")
        if not isinstance(message, str) or not isinstance(family_id, str) or family_id not in FAMILY_BY_ID:
            report.note("invalid entry")
            report.failures.append((index, "expected {message: str, family: known id}"))
            continue
        message = normalize_text(message)
        reasons = validate_message(message, "ne")
        words = message.split()
        if len(words) > MAX_WORDS:
            reasons = [*reasons, f"too many words ({len(words)})"]
        if reasons:
            report.note("invalid message")
            report.failures.append((index, "; ".join(reasons)))
            continue
        normalized = message.lower()
        if normalized in forbidden:
            report.note("benchmark collision")
            continue
        if normalized in existing or normalized in seen:
            report.note("duplicate")
            continue
        seen.add(normalized)
        family = FAMILY_BY_ID[family_id]
        case_id = f"{id_prefix}-{len(rows) + 1:04d}"
        business = TRAINING_BUSINESSES[(len(rows) + index) % len(TRAINING_BUSINESSES)]
        task = GenerationTask(
            id=case_id,
            family=family,
            language="ne",
            business=business,
            variant=0,
            prompt=build_prompt(business, family, "ne"),
        )
        rng = random.Random(f"{case_id}:{seed}")
        rows.append(build_case(task, message, rng, generator=generator).to_row())
        report.imported += 1
    return rows, report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="import an external message bank into cases")
    parser.add_argument("--input", type=Path, required=True, help="bank JSONL with message and family keys")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--id-prefix", default=DEFAULT_ID_PREFIX)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--corpus", type=Path, action="append", default=[], help="corpus JSONL to dedupe against")
    parser.add_argument("--benchmark", type=Path, action="append", default=[], help="benchmark JSON to avoid")
    args = parser.parse_args(argv)

    entries: list[Mapping[str, object]] = []
    skipped_lines: list[tuple[int, str]] = []
    for line_no, line in enumerate(args.input.read_text(encoding="utf-8-sig").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if not stripped.startswith("{"):
            skipped_lines.append((line_no, stripped[:60]))
            continue
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError as exc:
            skipped_lines.append((line_no, f"invalid JSON: {exc.msg}"))
            continue
        if not isinstance(parsed, Mapping):
            skipped_lines.append((line_no, "not an object"))
            continue
        entries.append(parsed)

    corpus_paths = tuple(args.corpus) or DEFAULT_CORPUS
    benchmark_paths = tuple(args.benchmark) or DEFAULT_BENCHMARK_PATHS
    rows, report = import_entries(
        entries,
        forbidden=benchmark_texts(benchmark_paths),
        existing=load_corpus_messages(corpus_paths),
        id_prefix=args.id_prefix,
        seed=args.seed,
    )
    report.skipped_lines = len(skipped_lines)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )
    print(f"wrote {args.out}")
    print(report.summary())
    for line_no, detail in skipped_lines[:10]:
        print(f"  line {line_no}: skipped ({detail})")
    for index, detail in report.failures[:10]:
        print(f"  entry {index}: {detail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
