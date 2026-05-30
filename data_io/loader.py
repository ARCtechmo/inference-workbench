"""Data loading for inference-workbench.

The only module that reads data files. Returns typed pandas DataFrames
(native pandas inference only) plus observed-fact metadata. Does not
clean, transform, or make analytical type judgments.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .exceptions import DataLoadError
from .metadata import DatasetMetadata


def _build_metadata(df: pd.DataFrame, source_path: str) -> DatasetMetadata:
    """Extract observed facts from a loaded DataFrame."""
    return DatasetMetadata(
        source_path=source_path,
        n_rows=int(df.shape[0]),
        n_cols=int(df.shape[1]),
        column_names=list(df.columns),
        dtypes={col: str(dtype) for col, dtype in df.dtypes.items()},
    )


def load_csv(path: str | Path) -> tuple[pd.DataFrame, DatasetMetadata]:
    """Load a CSV file into a DataFrame with native pandas type inference.

    Args:
        path: Path to the CSV file.

    Returns:
        A (DataFrame, DatasetMetadata) pair.

    Raises:
        DataLoadError: If the file is missing, unreadable, or unparseable.
    """
    p = Path(path)

    if not p.exists():
        raise DataLoadError(f"File not found: {p}")
    if not p.is_file():
        raise DataLoadError(f"Not a file: {p}")

    try:
        df = pd.read_csv(p)
    except pd.errors.EmptyDataError as exc:
        raise DataLoadError(f"File is empty or has no columns: {p}") from exc
    except pd.errors.ParserError as exc:
        raise DataLoadError(f"Could not parse as CSV: {p} ({exc})") from exc
    except (OSError, UnicodeDecodeError) as exc:
        raise DataLoadError(f"Could not read file: {p} ({exc})") from exc

    return df, _build_metadata(df, str(p))


def load_parquet(path: str | Path) -> tuple[pd.DataFrame, DatasetMetadata]:
    """Load a Parquet file. Deferred to v2 — not implemented."""
    raise NotImplementedError(
        "Parquet loading is deferred to v2. See FUTURE_FEATURES.md."
    )


def load_excel(path: str | Path) -> tuple[pd.DataFrame, DatasetMetadata]:
    """Load an Excel file. Deferred to v2 — not implemented."""
    raise NotImplementedError(
        "Excel loading is deferred to v2. See FUTURE_FEATURES.md."
    )
