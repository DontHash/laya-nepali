"""Machine-readable license lanes and provenance validation.

Mirrors ``docs/provenance.md``; the deterministic gate enforces what the docs
describe, so a row cannot reach ``data/export`` on an unrecorded lane.
"""

from __future__ import annotations

from typing import Any, Mapping

# Row-level license must be one of these (docs/provenance.md "Allowed lanes").
ALLOWED_LICENSES = ("CC-BY-4.0",)

# Substring match against ``provenance.source`` (case-insensitive).
BLOCKED_SOURCES = (
    "openslr54",
    "neptrans",
    "lyrics",
    "mp3pm",
    "wazam",
    "vectorscaling",
)

# Recorded in docs/provenance.md as "per-card - verify before use": hard-fail
# until the license is verified and the lane moves into the allowed table.
PENDING_SOURCES = ("kshitizgajurel", "foodmandu")

REQUIRED_FIELDS = ("source", "generator", "license")

# Informational: the generator recorded for LLM-assisted rows, e.g.
# ``gemini-3.5-flash-lite@2026-09-24``.
LLM_GENERATOR_PREFIX = "gemini-"


def provenance_failures(
    provenance: Mapping[str, Any] | None,
    *,
    require_reviewed: bool = False,
) -> list[str]:
    if not isinstance(provenance, Mapping) or not provenance:
        return ["provenance is required (source, generator, license)"]

    failures: list[str] = []
    for field_name in REQUIRED_FIELDS:
        value = provenance.get(field_name)
        if not isinstance(value, str) or not value.strip():
            failures.append(f"provenance.{field_name} must be a non-empty string")

    license_value = str(provenance.get("license", "")).strip().lower()
    allowed = {license_name.lower() for license_name in ALLOWED_LICENSES}
    if license_value and license_value not in allowed:
        failures.append(
            f"provenance.license {provenance.get('license')!r} is not an allowed lane "
            f"(allowed: {', '.join(ALLOWED_LICENSES)})"
        )

    source = str(provenance.get("source", "")).strip().lower()
    for blocked in BLOCKED_SOURCES:
        if blocked in source:
            failures.append(f"provenance.source {provenance.get('source')!r} is a blocked lane")
    for pending in PENDING_SOURCES:
        if pending in source:
            failures.append(
                f"provenance.source {provenance.get('source')!r} is pending license verification "
                "(see docs/provenance.md)"
            )

    if require_reviewed:
        reviewed_by = provenance.get("reviewed_by")
        if not isinstance(reviewed_by, str) or not reviewed_by.strip():
            failures.append("provenance.reviewed_by must be recorded before export")
    return failures
