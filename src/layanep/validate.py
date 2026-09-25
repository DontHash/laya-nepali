"""Dataset loading and dataset-level validation.

``load_cases`` accepts a JSONL file, a JSON array, or a directory containing
either (recursively), so both the reviewed export (true JSONL rows with
``state`` / ``questions`` / ``gold`` as JSON strings) and the readable golden
fixtures (nested objects) load through the same path.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable, Sequence

from .provenance import provenance_failures
from .schema import Case, SchemaError, validate_case

PII_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("email", re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")),
    ("url", re.compile(r"https?://\S+")),
    ("phone_np", re.compile(r"\+977[\s-]?\d{7,10}|\b9\d{9}\b")),
)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_rows(path: Path) -> list[dict[str, Any]]:
    if path.is_dir():
        rows: list[dict[str, Any]] = []
        for child in sorted(path.rglob("*")):
            if child.is_file() and child.suffix in {".jsonl", ".json"}:
                rows.extend(load_rows(child))
        return rows
    if not path.exists():
        raise FileNotFoundError(f"no dataset at {path}")
    if path.suffix == ".jsonl":
        rows = []
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SchemaError(f"{path}:{line_no}: invalid JSON ({exc.msg})") from exc
        return rows
    data = _read_json(path)
    if isinstance(data, list):
        return data
    if path.name.endswith(".manifest.json"):
        return []
    raise SchemaError(f"{path}: expected a JSON array or JSONL rows")


def load_cases(path: Path) -> list[Case]:
    return [Case.from_row(row) for row in load_rows(path)]


def find_duplicate_ids(cases: Iterable[Case]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for case in cases:
        if case.id in seen:
            duplicates.add(case.id)
        seen.add(case.id)
    return sorted(duplicates)


def scan_pii(text: str) -> list[str]:
    return [name for name, pattern in PII_PATTERNS if pattern.search(text)]


def case_pii_findings(case: Case) -> list[str]:
    """Scan every field of a case, not just the state and instructions."""
    findings: list[str] = []

    def scan(label: str, text: str) -> None:
        findings.extend(f"{label}:{name}" for name in scan_pii(text))

    scan("id", case.id)
    scan("workflow", case.workflow)
    scan("state", json.dumps(case.state, ensure_ascii=False))
    for qid, question in case.questions.items():
        scan(f"question {qid}", question.instructions)
        if question.criteria:
            scan(f"criteria {qid}", json.dumps(question.criteria, ensure_ascii=False))
    for qid, gold in case.gold.items():
        scan(f"gold {qid}", json.dumps(gold.to_dict(), ensure_ascii=False))
    scan("provenance", json.dumps(case.provenance, ensure_ascii=False))
    return findings


def validate_dataset(cases: Sequence[Case], *, require_reviewed: bool = False) -> list[str]:
    failures: list[str] = []
    duplicates = find_duplicate_ids(cases)
    if duplicates:
        failures.append(f"duplicate case ids: {duplicates}")
    for case in cases:
        try:
            validate_case(case)
        except SchemaError as exc:
            failures.append(str(exc))
            continue
        for finding in provenance_failures(case.provenance, require_reviewed=require_reviewed):
            failures.append(f"{case.id}: {finding}")
        findings = case_pii_findings(case)
        if findings:
            failures.append(f"{case.id}: PII pattern hit ({', '.join(findings)})")
    return failures


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validate a laya-nepali dataset against the pinned schema.")
    parser.add_argument("--data", type=Path, required=True, help="JSONL/JSON file or directory")
    parser.add_argument(
        "--require-reviewed",
        action="store_true",
        help="require provenance.reviewed_by (use for export data)",
    )
    args = parser.parse_args(argv)

    cases = load_cases(args.data)
    failures = validate_dataset(cases, require_reviewed=args.require_reviewed)
    decisions = sum(len(case.questions) for case in cases)
    if failures:
        print(f"FAIL: {len(failures)} problem(s) across {len(cases)} case(s)")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(f"PASS: {len(cases)} cases, {decisions} decisions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
