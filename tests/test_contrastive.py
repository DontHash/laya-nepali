"""Tests for the deterministic contrastive boundary builder."""

from __future__ import annotations

import json
from pathlib import Path

from layanep.contrastive import (
    BOUNDARIES,
    Boundary,
    _item_boundaries,
    build_rows,
    main,
)
from layanep.generate import validate_message
from layanep.schema import ABSTAIN_KEY, Case, validate_case
from layanep.templates import FAMILY_BY_ID


def all_boundaries() -> tuple[Boundary, ...]:
    return BOUNDARIES + _item_boundaries()


def test_build_rows_are_valid_and_unique() -> None:
    rows = build_rows(id_prefix="ne-test")
    assert len(rows) == sum(len(boundary.messages) for boundary in all_boundaries())
    ids = [row["id"] for row in rows]
    assert len(ids) == len(set(ids))
    for row in rows:
        case = Case.from_row(row)
        validate_case(case)
        reasons = validate_message(
            str(case.state.get("customer_message", "")),
            str(case.provenance.get("language", "")),
        )
        assert reasons == [], (case.id, reasons)


def test_boundary_families_and_gold() -> None:
    rows = build_rows(id_prefix="ne-test")
    by_family: dict[str, list[dict]] = {}
    for row in rows:
        family = str((row.get("provenance") or {}).get("family", ""))
        by_family.setdefault(family, []).append(row)

    for family_id in {boundary.family_id for boundary in all_boundaries()}:
        assert family_id in FAMILY_BY_ID
        assert by_family.get(family_id), f"no rows for {family_id}"

    for row in by_family["refund_status"]:
        gold = json.loads(row["gold"]) if isinstance(row["gold"], str) else row["gold"]
        assert gold["command"]["label"] == ABSTAIN_KEY
        assert gold["needs_staff"]["label"] == "true"
        assert gold["abstain"]["label"] == "true"

    for row in by_family["bare_order"]:
        gold = json.loads(row["gold"]) if isinstance(row["gold"], str) else row["gold"]
        assert gold["command"]["label"] == ABSTAIN_KEY
        assert gold["order_intent"]["label"] == "true"
        assert gold["abstain"]["label"] == "true"

    for row in by_family["query_price"]:
        gold = json.loads(row["gold"]) if isinstance(row["gold"], str) else row["gold"]
        assert gold["command"]["label"] == "price"
        assert gold["query_field"]["label"] == "price"


def test_cli_writes_selected_boundaries(tmp_path: Path) -> None:
    out = tmp_path / "contrastive.jsonl"
    rc = main(["--out", str(out), "--id-prefix", "ne-cli", "--boundaries", "item_query_triangle"])
    assert rc == 0
    rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert rows
    assert all(row["id"].startswith("ne-cli-") for row in rows)
    assert {row["provenance"]["family"] for row in rows} == {
        "query_price",
        "query_availability",
        "query_details",
    }
