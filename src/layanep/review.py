"""Ground-truth review of generated candidates (P1, critical path).

Candidates from ``data/generated/`` become a JSONL review sheet in
``data/reviewed/``: one record per candidate carrying the decision
(accept/edit/reject), the reviewer and the reason. ``apply`` writes the
accepted and edited rows with ``provenance.reviewed_by`` set; those are the
only rows eligible for export.

Typical flow::

    python -m layanep.review build --reviewer NAME
    python -m layanep.review run --reviewer NAME          # interactive, saves as you go
    python -m layanep.review list --status pending
    python -m layanep.review set --id ne-gen-0001 --action edit --text "मोमोको मूल्य कति?"
    python -m layanep.review apply
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from .generate import validate_message
from .normalize import normalize_text
from .provenance import provenance_failures
from .schema import ABSTAIN_KEY, Case, SchemaError, validate_case
from .templates import FAMILY_BY_ID
from .validate import load_rows

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = REPO_ROOT / "data" / "generated" / "ne-candidates.jsonl"
DEFAULT_SHEET = REPO_ROOT / "data" / "reviewed" / "ne-decisions-v1.review.jsonl"
DEFAULT_APPLIED = REPO_ROOT / "data" / "reviewed" / "ne-decisions-v1.jsonl"
REVIEW_REVISION = "review-v1"
STATUSES = ("pending", "accepted", "edited", "rejected")
ACTIONS = {"accept": "accepted", "edit": "edited", "reject": "rejected"}


def default_reviewer() -> str:
    env = os.environ.get("REVIEWER", "").strip()
    if env:
        return env
    try:
        completed = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True,
            text=True,
            check=True,
        )
        if completed.stdout.strip():
            return completed.stdout.strip()
    except Exception:  # noqa: BLE001 - a missing git config is not a failure
        pass
    return "reviewer"


@dataclass
class ReviewRecord:
    id: str
    status: str = "pending"
    text: str = ""
    original_text: str = ""
    note: str = ""
    reviewed_by: str | None = None
    reviewed_at: str | None = None
    needs_human: bool = True
    review_mode: str = "human"
    case: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ReviewRecord":
        return cls(
            id=str(data.get("id", "")),
            status=str(data.get("status", "pending")),
            text=str(data.get("text", "")),
            original_text=str(data.get("original_text", "")),
            note=str(data.get("note", "")),
            reviewed_by=data.get("reviewed_by"),
            reviewed_at=data.get("reviewed_at"),
            needs_human=bool(data.get("needs_human", True)),
            review_mode=str(data.get("review_mode", "human")),
            case=dict(data.get("case") or {}),
        )


@dataclass
class ApplyReport:
    written: int = 0
    skipped_pending: int = 0
    skipped_rejected: int = 0
    failures: list[tuple[str, list[str]]] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"written {self.written} | pending {self.skipped_pending} | "
            f"rejected {self.skipped_rejected} | invalid {len(self.failures)}"
        )


def load_sheet(path: Path) -> list[ReviewRecord]:
    if not path.exists():
        return []
    records: list[ReviewRecord] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            records.append(ReviewRecord.from_dict(json.loads(line)))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSON ({exc.msg})") from exc
    return records


def save_sheet(path: Path, records: Sequence[ReviewRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as sink:
        for record in records:
            sink.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")


def case_message(case_row: dict) -> str:
    return str(Case.from_row(case_row).state.get("customer_message", ""))


def _expected_summary(case_row: dict) -> str:
    case = Case.from_row(case_row)
    return (
        f"command={case.gold['command'].label} | query_field={case.gold['query_field'].label} | "
        f"order_intent={case.gold['order_intent'].label} | needs_staff={case.gold['needs_staff'].label} | "
        f"abstain={case.gold['abstain'].label}"
    )


def _needs_human(case_row: dict, record_id: str, sample_rate: float) -> bool:
    provenance = case_row.get("provenance") or {}
    family = FAMILY_BY_ID.get(str(provenance.get("family", "")))
    if family is None or family.command == ABSTAIN_KEY:
        return True
    if sample_rate >= 1.0:
        return True
    if sample_rate <= 0.0:
        return False
    digest = hashlib.sha1(record_id.encode("utf-8")).hexdigest()
    return int(digest, 16) % 100 < int(round(sample_rate * 100))


def build_sheet(input_path: Path, sheet_path: Path, *, sample_rate: float = 1.0) -> list[ReviewRecord]:
    existing = {record.id: record for record in load_sheet(sheet_path)}
    records: list[ReviewRecord] = []
    for row in load_rows(input_path):
        case = Case.from_row(row)
        message = case_message(row)
        record = existing.get(case.id)
        if record is None:
            record = ReviewRecord(
                id=case.id,
                text=message,
                original_text=message,
                needs_human=_needs_human(row, case.id, sample_rate),
            )
        record.case = row
        records.append(record)
    save_sheet(sheet_path, records)
    return records


def format_record(record: ReviewRecord, index: int | None = None, total: int | None = None) -> str:
    case = Case.from_row(record.case)
    provenance = case.provenance
    header = f"{record.id}  {provenance.get('family', '?')} / {provenance.get('language', '?')}"
    if index is not None and total is not None:
        header = f"[{index}/{total}] " + header
    lines = [
        f"{header}  ({record.status})",
        f"  text: {record.text}",
    ]
    if record.status == "edited":
        lines.append(f"  was:  {record.original_text}")
    family = FAMILY_BY_ID.get(str(provenance.get("family", "")))
    if family:
        lines.append(f"  should express: {family.instruction}")
    lines.append(f"  expected: {_expected_summary(record.case)}")
    lines.append(f"  review: {'human' if record.needs_human else 'judge auto'}")
    lines.append(f"  generator: {provenance.get('generator', '?')}")
    if record.note:
        lines.append(f"  note: {record.note}")
    return "\n".join(lines)


def set_decision(
    record: ReviewRecord,
    action: str,
    *,
    reviewer: str,
    text: str | None = None,
    note: str = "",
) -> ReviewRecord:
    if record.status != "pending":
        raise ValueError(f"{record.id} is already {record.status}")
    if action not in ACTIONS:
        raise ValueError(f"unknown action {action!r} (use accept, edit or reject)")
    record.status = ACTIONS[action]
    record.reviewed_by = reviewer
    record.reviewed_at = datetime.now(timezone.utc).isoformat()
    record.note = note
    if action == "edit":
        if not text or not normalize_text(text):
            raise ValueError("edit requires --text with the corrected message")
        record.text = normalize_text(text)
    else:
        record.text = normalize_text(record.text)
    return record


def apply_sheet(records: Sequence[ReviewRecord], out_path: Path) -> ApplyReport:
    report = ApplyReport()
    auto_timestamp = datetime.now(timezone.utc).isoformat()
    for record in records:
        if record.status == "pending" and not record.needs_human:
            record.status = "accepted"
            record.reviewed_by = "llm-judge"
            record.reviewed_at = auto_timestamp
            record.review_mode = "judge-auto"
            record.note = record.note or "auto-accepted: judge pass + sampled human review"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as sink:
        for record in records:
            if record.status == "pending":
                report.skipped_pending += 1
                continue
            if record.status == "rejected":
                report.skipped_rejected += 1
                continue
            case = Case.from_row(record.case)
            message = normalize_text(record.text)
            language = str(case.provenance.get("language", ""))
            business_name = str((case.state.get("business") or {}).get("name", "")) or None
            failures = validate_message(message, language, business_name) if language else []
            if not failures:
                case.state["customer_message"] = message
                case.provenance["reviewed_by"] = record.reviewed_by
                case.provenance["reviewed_at"] = record.reviewed_at
                case.provenance["review"] = record.status
                case.provenance["review_mode"] = record.review_mode
                failures = provenance_failures(case.provenance, require_reviewed=True)
            if not failures:
                try:
                    validate_case(case)
                except SchemaError as exc:
                    failures = [str(exc)]
            if failures:
                report.failures.append((record.id, failures))
                continue
            sink.write(json.dumps(case.to_row(), ensure_ascii=False) + "\n")
            report.written += 1
    return report


def filter_records(
    records: Sequence[ReviewRecord],
    *,
    status: str | None = None,
    family: str | None = None,
    language: str | None = None,
) -> list[ReviewRecord]:
    def keep(record: ReviewRecord) -> bool:
        if status and record.status != status:
            return False
        if family and record.case.get("provenance", {}).get("family") != family:
            return False
        if language and record.case.get("provenance", {}).get("language") != language:
            return False
        return True

    return [record for record in records if keep(record)]


def run_review(
    records: list[ReviewRecord],
    sheet_path: Path,
    reviewer: str,
    limit: int | None,
    *,
    include_all: bool = False,
) -> int:
    pending = [
        record
        for record in records
        if record.status == "pending" and (include_all or record.needs_human)
    ]
    if limit:
        pending = pending[:limit]
    if not pending:
        print("nothing pending for human review (judge-passed rows are auto-accepted at apply)")
        return 0
    print("Accept when the message is natural and expresses exactly the intent above.")
    print("Edit to fix the wording; reject when it is wrong, unnatural or unsafe.")
    print("commands: [a]ccept  [e]dit  [r]eject  [s]kip  [q]uit")
    for index, record in enumerate(pending, start=1):
        print()
        print(format_record(record, index=index, total=len(pending)))
        while True:
            try:
                command = input("[a/e/r/s/q] > ").strip()
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
            print("commands: [a]ccept  [e]dit  [r]eject  [s]kip  [q]uit")
    return 0


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--sheet", type=Path, default=DEFAULT_SHEET, help="review sheet JSONL")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review generated Nepali candidates.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build", help="create or refresh the review sheet")
    build.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    build.add_argument(
        "--sample-rate",
        type=float,
        default=0.25,
        help="share of judge-passed command-kind rows that still need human review (safety rows are always human)",
    )
    _add_common(build)

    listing = subparsers.add_parser("list", help="list review records")
    listing.add_argument("--status", choices=STATUSES, default=None)
    listing.add_argument("--family", default=None)
    listing.add_argument("--language", default=None)
    listing.add_argument("--limit", type=int, default=0)
    _add_common(listing)

    show = subparsers.add_parser("show", help="show one record")
    show.add_argument("--id", required=True)
    _add_common(show)

    run = subparsers.add_parser("run", help="interactive review loop")
    run.add_argument("--reviewer", default=None)
    run.add_argument("--limit", type=int, default=0)
    run.add_argument("--status", choices=STATUSES, default="pending")
    run.add_argument("--family", default=None)
    run.add_argument("--language", default=None)
    run.add_argument("--all", action="store_true", help="also review judge-auto rows")
    _add_common(run)

    setter = subparsers.add_parser("set", help="record one decision")
    setter.add_argument("--id", required=True)
    setter.add_argument("--action", choices=tuple(ACTIONS), required=True)
    setter.add_argument("--text", default=None)
    setter.add_argument("--note", default="")
    setter.add_argument("--reviewer", default=None)
    _add_common(setter)

    apply_parser = subparsers.add_parser("apply", help="write accepted rows with reviewed_by set")
    apply_parser.add_argument("--out", type=Path, default=DEFAULT_APPLIED)
    _add_common(apply_parser)

    args = parser.parse_args(argv)
    reviewer = getattr(args, "reviewer", None) or default_reviewer()

    if args.command == "build":
        records = build_sheet(args.input, args.sheet, sample_rate=args.sample_rate)
        pending = sum(1 for record in records if record.status == "pending")
        human = sum(1 for record in records if record.status == "pending" and record.needs_human)
        print(f"sheet {args.sheet}: {len(records)} records ({pending} pending, {human} need human review)")
        return 0

    records = load_sheet(args.sheet)
    if not records:
        print(f"no records in {args.sheet}; run `build` first")
        return 1

    if args.command == "list":
        selected = filter_records(
            records, status=args.status, family=args.family, language=args.language
        )
        if args.limit:
            selected = selected[: args.limit]
        for record in selected:
            case = Case.from_row(record.case)
            print(
                f"{record.id}  {record.status:8}  {case.provenance.get('family', '?'):18} "
                f"{case.provenance.get('language', '?'):7}  {record.text}"
            )
        print(f"{len(selected)} record(s)")
        return 0

    if args.command == "show":
        for record in records:
            if record.id == args.id:
                print(format_record(record))
                return 0
        print(f"{args.id} not found")
        return 1

    if args.command == "run":
        print(f"reviewer: {reviewer}")
        selected = filter_records(records, status=args.status, family=args.family, language=args.language)
        return run_review(selected, args.sheet, reviewer, args.limit or None, include_all=args.all)

    if args.command == "set":
        for record in records:
            if record.id == args.id:
                try:
                    set_decision(record, args.action, reviewer=reviewer, text=args.text, note=args.note)
                except ValueError as exc:
                    print(str(exc))
                    return 1
                save_sheet(args.sheet, records)
                print(f"{record.id} -> {record.status}")
                return 0
        print(f"{args.id} not found")
        return 1

    if args.command == "apply":
        report = apply_sheet(records, args.out)
        save_sheet(args.sheet, records)
        print(report.summary())
        for record_id, failures in report.failures[:10]:
            print(f"  invalid {record_id}: {', '.join(failures)}")
        if report.written:
            print(f"wrote {args.out}")
        return 0 if report.written or not report.failures else 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
