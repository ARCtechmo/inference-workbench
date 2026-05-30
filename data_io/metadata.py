"""Observed-fact metadata for a loaded dataset.

This records what was read, not any analytical judgment about it.
Type *proposals* (binary, categorical, ordinal) are the profile layer's
job, not data_io's.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class DatasetMetadata:
    """Facts observed at load time. No analysis, no judgment."""

    source_path: str
    n_rows: int
    n_cols: int
    column_names: list[str]
    dtypes: dict[str, str]  # column name -> native pandas dtype as string
    loaded_at: datetime = field(default_factory=datetime.now)
