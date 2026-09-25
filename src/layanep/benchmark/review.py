"""Human review of benchmark steps (P1a, critical path).

The Devanagari benchmark is the yardstick, so every step gets a human pass:
accept, edit the text, relabel the expected kind, or reject. ``apply`` rewrites
the corpus file with the reviewed text/labels, drops rejected steps, records
the review in the corpus meta, and validates the frozen corpus before the file
is replaced.

Typical flow::

    python -m layanep.benchmark.review build
    python -m layanep.benchmark.review run --reviewer NAME   # interactive, saves as you go
    python -m layanep.benchmark.review apply                 # freezes the corpus
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from ..normalize import normalize_text
from ..review import default_reviewer
from ..schema import LU_COMMAND_KINDS
from .corpus import REPO_ROOT, load_corpus, validate_corpus

DEFAULT_CORPUS = REPO_ROOT / "data" / "benchmark" / "ne-bench-deva-v2.json"
DEFAULT_SHEET = REPO_ROOT / "data" / "benchmark" / "ne-bench-deva-v2.review.jsonl"
REVIEW_REVISION = "bench-deva-review-v1"
STATUSES = ("pending", "accepted", "edited", "rejected")
ACTIONS = ("accept", "edit", "relabel", "reject")
ABSTAIN_LABELS = ("none", "abstain", "")


@dataclass
class StepRecord:
    step_id: str
    case_id: str = ""
    menu_id: str = ""
    description: str = ""
    status: str = "pending"
    text: str = ""
    original_text: str = ""
    expected: str | None = None
    original_expected: str | None = None
    note: str = ""
    reviewed_by: str | None = None
    reviewed_at: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "StepRecord":
        return cls(
            step_id=str(data.get("step_id", "")),
            case_id=str(data.get("case_id", "")),
            menu_id=str(data.get("menu_id", "")),
            description=str(data.get("description", "")),
            status=str(data.get("status", "pending")),
            text=str(data.get("text", "")),
            original_text=str(data.get("original_text", "")),
            expected=data.get("expected"),
            original_expected=data.get("original_expected"),
            note=str(data.get("note", "")),
            reviewed_by=data.get("reviewed_by"),
            reviewed_at=data.get("reviewed_at"),
        )

    @property
    def changed(self) -> bool:
        return self.text != self.original_text or self.expected != self.original_expected


def load_sheet(path: Path) -> list[StepRecord]:
    if not path.exists():
        return []
    records: list[StepRecord] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            records.append(StepRecord.from_dict(json.loads(line)))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSON ({exc.msg})") from exc
    return records


def save_sheet(path: Path, records: Sequence[StepRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as sink:
        for record in records:
            sink.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")


def build_sheet(corpus_path: Path, sheet_path: Path) -> list[StepRecord]:
    existing = {record.step_id: record for record in load_sheet(sheet_path)}
    corpus = load_corpus(corpus_path)
    records: list[StepRecord] = []
    for case in corpus.cases:
        for step in case.steps:
            record = existing.get(step.id)
            if record is None:
                record = StepRecord(
                    step_id=step.id,
                    original_text=step.text,
                    text=step.text,
                    original_expected=step.expected,
                    expected=step.expected,
                )
            record.case_id = case.id
            record.menu_id = case.menu_id
            record.description = case.description
            records.append(record)
    save_sheet(sheet_path, records)
    return records


def format_record(record: StepRecord, index: int | None = None, total: int | None = None) -> str:
    header = f"{record.step_id}  {record.case_id}  ({record.status})"
    if index is not None and total is not None:
        header = f"[{index}/{total}] " + header
    expected = record.expected or "abstain"
    lines = [header, f"  text: {record.text}", f"  expected: {expected}", f"  case: {record.description}"]
    if record.changed:
        lines.append(f"  was: {record.original_text!r} -> {record.original_expected or 'abstain'}")
    if record.note:
        lines.append(f"  note: {record.note}")
    return "\n".join(lines)


def set_decision(
    record: StepRecord,
    action: str,
    *,
    reviewer: str,
    text: str | None = None,
    expected: str | None = None,
    note: str = "",
) -> StepRecord:
    if record.status != "pending":
        raise ValueError(f"{record.step_id} is already {record.status}")
    if action not in ACTIONS:
        raise ValueError(f"unknown action {action!r} (use {', '.join(ACTIONS)})")
    record.reviewed_by = reviewer
    record.reviewed_at = datetime.now(timezone.utc).isoformat()
    record.note = note

    if action == "reject":
        record.status = "rejected"
        return record

    if action == "accept":
        record.status = "accepted"
        return record

    if action == "edit":
        if not text or not normalize_text(text):
            raise ValueError("edit requires --text with the corrected step")
        record.text = normalize_text(text)
    elif action == "relabel":
        if expected is None:
            raise ValueError("relabel requires --expected with a kind or 'none'")
        record.expected = None if expected in ABSTAIN_LABELS else expected
        if record.expected is not None and record.expected not in LU_COMMAND_KINDS:
            raise ValueError(f"--expected must be a kind or 'none', got {expected!r}")

    record.status = "edited" if record.changed else "accepted"
    return record


def apply_sheet(corpus_path: Path, records: Sequence[StepRecord], *, allow_pending: bool = False) -> str:
    pending = [record for record in records if record.status == "pending"]
    if pending and not allow_pending:
        raise ValueError(f"{len(pending)} step(s) still pending; finish the review or pass --allow-pending")

    by_id = {record.step_id: record for record in records}
    raw = json.loads(corpus_path.read_text(encoding="utf-8"))
    counts = {"accepted": 0, "edited": 0, "rejected": 0, "pending": len(pending)}
    cases = []
    reviewer = None
    reviewed_at = None
    for case in raw["cases"]:
        steps = []
        for step in case["steps"]:
            record = by_id.get(step["id"])
            if record is None:
                raise ValueError(f"{step['id']}: no review record (run `build` first)")
            if record.status == "pending":
                steps.append(step)
                continue
            if record.status == "rejected":
                counts["rejected"] += 1
                continue
            updated = dict(step)
            updated["text"] = normalize_text(record.text)
            updated["expected"] = record.expected
            updated["reviewed"] = True
            steps.append(updated)
            counts["edited" if record.status == "edited" else "accepted"] += 1
            reviewer = record.reviewed_by
            reviewed_at = record.reviewed_at
        if steps:
            case = dict(case)
            case["steps"] = steps
            cases.append(case)

    raw["cases"] = cases
    raw["review"] = {
        "reviewed_by": reviewer,
        "reviewed_at": reviewed_at,
        **counts,
    }

    temp_path = corpus_path.with_suffix(".tmp.json")
    temp_path.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    failures = validate_corpus(load_corpus(temp_path))
    if failures:
        temp_path.unlink(missing_ok=True)
        raise ValueError("frozen corpus is invalid: " + "; ".join(failures))
    os.replace(temp_path, corpus_path)
    return f"frozen {corpus_path.name}: {counts['accepted']} accepted, {counts['edited']} edited, {counts['rejected']} rejected"


def filter_records(
    records: Sequence[StepRecord],
    *,
    status: str | None = None,
    case_id: str | None = None,
) -> list[StepRecord]:
    def keep(record: StepRecord) -> bool:
        if status and record.status != status:
            return False
        if case_id and record.case_id != case_id:
            return False
        return True

    return [record for record in records if keep(record)]


def run_review(records: list[StepRecord], sheet_path: Path, reviewer: str, limit: int | None) -> int:
    queue = [record for record in records if record.status == "pending"]
    if limit:
        queue = queue[:limit]
    if not queue:
        print("nothing pending")
        return 0
    print("Accept when the step is clear and correctly labeled; edit the text, relabel the kind, or reject.")
    print("commands: [a]ccept  [e]dit  [l]abel  [r]eject  [s]kip  [q]uit")
    for index, record in enumerate(queue, start=1):
        print()
        print(format_record(record, index=index, total=len(queue)))
        while True:
            try:
                command = input("[a/e/l/r/s/q] > ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                return 0
            if command in ("q", "quit"):
                return 0
            if command in ("s", "skip", ""):
                break
            if command in ("a", "accept"):
                set_decision(record, "accept", reviewer=reviewer)
                save_sheet(sheet_path, records)
                print("  accepted")
                break
            if command in ("r", "reject"):
                try:
                    note = input("reason (optional) > ").strip()
                except (EOFError, KeyboardInterrupt):
                    print()
                    return 0
                set_decision(record, "reject", reviewer=reviewer, note=note)
                save_sheet(sheet_path, records)
                print("  rejected")
                break
            if command in ("l", "label", "relabel"):
                print("  kinds: " + ", ".join(LU_COMMAND_KINDS) + ", none")
                try:
                    expected = input("new label > ").strip()
                except (EOFError, KeyboardInterrupt):
                    print()
                    return 0
                try:
                    set_decision(record, "relabel", reviewer=reviewer, expected=expected)
                except ValueError as exc:
                    print(f"  {exc}")
                    continue
                save_sheet(sheet_path, records)
                print(f"  relabeled -> {record.expected or 'abstain'}")
                break
            if command in ("e", "edit"):
                try:
                    text = input("new text > ").strip()
                except (EOFError, KeyboardInterrupt):
                    print()
                    return 0
                try:
                    set_decision(record, "edit", reviewer=reviewer, text=text)
                except ValueError as exc:
                    print(f"  {exc}")
                    continue
                save_sheet(sheet_path, records)
                print("  edited")
                break
            print("commands: [a]ccept  [e]dit  [l]abel  [r]eject  [s]kip  [q]uit")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review Devanagari benchmark steps.")
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--sheet", type=Path, default=DEFAULT_SHEET)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("build", help="create or refresh the review sheet")

    listing = subparsers.add_parser("list", help="list review records")
    listing.add_argument("--status", choices=STATUSES, default=None)
    listing.add_argument("--case", default=None)
    listing.add_argument("--limit", type=int, default=0)

    show = subparsers.add_parser("show", help="show one record")
    show.add_argument("--id", required=True)

    run = subparsers.add_parser("run", help="interactive review loop")
    run.add_argument("--reviewer", default=None)
    run.add_argument("--limit", type=int, default=0)

    setter = subparsers.add_parser("set", help="record one decision")
    setter.add_argument("--id", required=True)
    setter.add_argument("--action", choices=ACTIONS, required=True)
    setter.add_argument("--text", default=None)
    setter.add_argument("--expected", default=None)
    setter.add_argument("--note", default="")
    setter.add_argument("--reviewer", default=None)

    apply_parser = subparsers.add_parser("apply", help="freeze the corpus from the sheet")
    apply_parser.add_argument("--allow-pending", action="store_true")

    args = parser.parse_args(argv)
    reviewer = getattr(args, "reviewer", None) or default_reviewer()

    if args.command == "build":
        records = build_sheet(args.corpus, args.sheet)
        pending = sum(1 for record in records if record.status == "pending")
        print(f"sheet {args.sheet}: {len(records)} records ({pending} pending)")
        return 0

    records = load_sheet(args.sheet)
    if not records:
        print(f"no records in {args.sheet}; run `build` first")
        return 1

    if args.command == "list":
        selected = filter_records(records, status=args.status, case_id=args.case)
        if args.limit:
            selected = selected[: args.limit]
        for record in selected:
            print(
                f"{record.step_id:20} {record.status:8} {record.expected or 'abstain':28} {record.text}"
            )
        print(f"{len(selected)} record(s)")
        return 0

    if args.command == "show":
        for record in records:
            if record.step_id == args.id:
                print(format_record(record))
                return 0
        print(f"{args.id} not found")
        return 1

    if args.command == "run":
        print(f"reviewer: {reviewer}")
        return run_review(records, args.sheet, reviewer, args.limit or None)

    if args.command == "set":
        for record in records:
            if record.step_id == args.id:
                try:
                    set_decision(
                        record,
                        args.action,
                        reviewer=reviewer,
                        text=args.text,
                        expected=args.expected,
                        note=args.note,
                    )
                except ValueError as exc:
                    print(str(exc))
                    return 1
                save_sheet(args.sheet, records)
                print(f"{record.step_id} -> {record.status}")
                return 0
        print(f"{args.id} not found")
        return 1

    if args.command == "apply":
        try:
            print(apply_sheet(args.corpus, records, allow_pending=args.allow_pending))
        except ValueError as exc:
            print(str(exc))
            return 1
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
