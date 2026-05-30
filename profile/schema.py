"""Result schema for the profile layer.

A ProfileResult is a bag of observed findings. The profile layer surfaces
issues; it does not fix them. Type proposals are *structural* only —
ordinal/nominal/role classification is the analyst's job (workflow step).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ColumnProfile:
    """Per-column findings, assembled by the orchestrator."""

    name: str
    native_dtype: str
    proposed_type: str          # continuous | binary | count | categorical | empty
    n_missing: int
    pct_missing: float
    n_unique: int
    is_near_constant: bool
    is_high_cardinality: bool
    n_outliers: int             # 0 for non-continuous columns


@dataclass(frozen=True)
class ProfileResult:
    """Full profile of a dataset. Surfaces issues; does not fix them."""

    n_rows: int
    n_cols: int
    columns: dict[str, ColumnProfile]

    def flagged_columns(self) -> list[str]:
        """Columns with at least one surfaced issue, for quick triage."""
        return [
            name
            for name, c in self.columns.items()
            if c.n_missing > 0
            or c.is_near_constant
            or c.is_high_cardinality
            or c.n_outliers > 0
            or c.proposed_type == "empty"
        ]
