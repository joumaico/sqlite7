"""SQLite-specific SQL builders and conflict policies."""

from __future__ import annotations

from typing import Literal

ConflictPolicy = Literal["abort", "fail", "ignore", "replace", "rollback"]
_VALID_POLICIES = {"abort", "fail", "ignore", "replace", "rollback"}


def normalize_conflict_policy(policy: str | None) -> str:
    """Normalize a conflict policy string.

    Args:
        policy: Requested policy.

    Returns:
        Lowercase SQLite conflict policy.

    Raises:
        ValueError: If the policy is unknown.
    """

    candidate = (policy or "abort").strip().lower()
    if candidate not in _VALID_POLICIES:
        raise ValueError(
            f"Unsupported conflict policy {policy!r}. Choose one of: {sorted(_VALID_POLICIES)!r}"
        )
    return candidate


def insert_keyword(policy: str | None) -> str:
    """Return the proper INSERT prefix for a conflict policy."""

    normalized = normalize_conflict_policy(policy)
    if normalized == "abort":
        return "INSERT"
    return f"INSERT OR {normalized.upper()}"
