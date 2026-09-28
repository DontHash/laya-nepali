"""Commerce domains.

Each subpackage is one domain (restaurant, clothing, ...) and binds the same
surface, so the pipeline and serving layer stay domain-agnostic:

- ``DOMAIN_NAME`` — registry key.
- ``WORKFLOW`` — dataset workflow id used in rows and exports.
- ``questions(business_name)`` — builds the typed question set.
- ``T0_READ_ONLY`` / ``T1_MUTATIONS`` — autonomy tier vocabularies.
- ``DEFAULT_CONFIDENCE_TAU`` / ``DEFAULT_P_NONE_MAX`` — calibration defaults.
- ``classify_tier`` / ``extract_signals`` — the shared tier engine
  (``policy_core.py``) bound to this domain's vocabulary.
- ``RESPONSE_TEMPLATES`` / ``fill_template`` / ``escalation_message`` — the
  shared response engine (``responses_core.py``) bound to this domain.
- ``generator`` — synthetic training data: businesses, families, prompts,
  plans, gold and case building.

See ``docs/domains.md`` for the checklist to add a new domain.
"""

from __future__ import annotations

import pkgutil
from importlib import import_module
from types import ModuleType

_PACKAGE = __name__
_cache: dict[str, ModuleType] = {}
_workflow_cache: dict[str, ModuleType] | None = None


def available_domains() -> list[str]:
    """Return the installed domain package names, sorted."""
    return sorted(module.name for module in pkgutil.iter_modules(__path__) if module.ispkg)


def get_domain(name: str) -> ModuleType:
    """Return the domain package for ``name``.

    Raises ``KeyError`` when the domain is not installed.
    """
    if name not in _cache:
        if name not in available_domains():
            raise KeyError(f"unknown domain {name!r}; available: {', '.join(available_domains())}")
        _cache[name] = import_module(f"{_PACKAGE}.{name}")
    return _cache[name]


def workflow_map() -> dict[str, ModuleType]:
    """Return ``workflow id -> domain package`` for every installed domain."""
    global _workflow_cache
    if _workflow_cache is None:
        _workflow_cache = {get_domain(name).WORKFLOW: get_domain(name) for name in available_domains()}
    return _workflow_cache
