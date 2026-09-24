"""Dataset generation pipeline (P1).

Turns license-clean sources, templates and translations into candidate cases in
the pinned schema. Populated in P1; see docs/provenance.md for the allowed
source lanes.
"""

from __future__ import annotations

from .schema import DATASET_REVISION

GENERATOR_REVISION = f"{DATASET_REVISION}-gen0"
