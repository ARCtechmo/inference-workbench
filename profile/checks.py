"""The seven profile checks plus an orchestrator.

Each check is independently callable and unit-testable. profile() runs
them all and assembles a ProfileResult. Surfaces issues; never fixes.
"""

from __future__ import annotations

import pandas as pd
from pandas.api import types as ptypes

from .schema import ColumnProfile, ProfileResult

# --- Tunable thresholds (surface-level heuristics, not hard rules) ---
NEAR_CONSTANT_PCT = 0.95       # most-frequent value covers >= this share
HIGH_CARD_ABS = 50             # > this many unique values
HIGH_CARD_REL = 0.50           # or unique count > this share of rows
COUNT_MAX_RANGE = 100          # non-neg int with range <= this -> "count"
IQR_MULTIPLIER = 1.5


def check_missingness(series: pd.Series) -> tuple[int, float]:
    """Return (n_missing, pct_missing) for a column."""
    n_missing = int(series.isna().sum())
    pct = float(n_missing / len(series)) if len(series) else 0.0
    return n_missing, pct


def count_unique(series: pd.Series) -> int:
    """Number of distinct non-null values."""
    return int(series.nunique(dropna=True))


def propose_type(series: pd.Series) -> str:
    """Propose a STRUCTURAL type. No ordinal detection — that is the
    analyst's call during classification.

    Returns one of: empty | binary | continuous | count | categorical.
    """
    non_null = series.dropna()
    if non_null.empty:
        return "empty"

    n_unique = non_null.nunique()
    if n_unique == 2:
        return "binary"

    if ptypes.is_float_dtype(series):
        return "continuous"

    if ptypes.is_integer_dtype(series):
        # Non-negative integer with a modest range reads as a count;
        # otherwise treat as continuous. Heuristic, surfaced for review.
        if non_null.min() >= 0 and (non_null.max() - non_null.min()) <= COUNT_MAX_RANGE:
            return "count"
        return "continuous"

    # str/object/categorical and everything else
    return "categorical"


def is_near_constant(series: pd.Series, threshold: float = NEAR_CONSTANT_PCT) -> bool:
    """True if the most-frequent non-null value covers >= threshold share."""
    non_null = series.dropna()
    if non_null.empty:
        return False
    top_share = non_null.value_counts(normalize=True).iloc[0]
    return bool(top_share >= threshold)


def is_high_cardinality(
    series: pd.Series,
    abs_threshold: int = HIGH_CARD_ABS,
    rel_threshold: float = HIGH_CARD_REL,
) -> bool:
    """True for categorical-like columns with many distinct values
    (absolute) or near-unique values (relative — likely an ID column).
    Only meaningful for non-numeric columns."""
    if ptypes.is_numeric_dtype(series):
        return False
    non_null = series.dropna()
    if non_null.empty:
        return False
    n_unique = non_null.nunique()
    if n_unique > abs_threshold:
        return True
    return bool(n_unique / len(non_null) > rel_threshold)


def count_outliers(series: pd.Series, multiplier: float = IQR_MULTIPLIER) -> int:
    """IQR-based outlier count. Continuous/numeric columns only; 0 otherwise."""
    if not ptypes.is_numeric_dtype(series):
        return 0
    non_null = series.dropna()
    if non_null.empty:
        return 0
    q1, q3 = non_null.quantile(0.25), non_null.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return 0
    lower, upper = q1 - multiplier * iqr, q3 + multiplier * iqr
    return int(((non_null < lower) | (non_null > upper)).sum())


def profile(df: pd.DataFrame) -> ProfileResult:
    """Run all checks and assemble a ProfileResult.

    This is the entry point the workflow layer calls. Surfaces issues;
    does not fix them.
    """
    columns: dict[str, ColumnProfile] = {}
    for name in df.columns:
        s = df[name]
        n_missing, pct_missing = check_missingness(s)
        ptype = propose_type(s)
        columns[name] = ColumnProfile(
            name=str(name),
            native_dtype=str(s.dtype),
            proposed_type=ptype,
            n_missing=n_missing,
            pct_missing=pct_missing,
            n_unique=count_unique(s),
            is_near_constant=is_near_constant(s),
            is_high_cardinality=is_high_cardinality(s),
            # Outliers only meaningful for continuous; skip binary/count noise
            n_outliers=count_outliers(s) if ptype == "continuous" else 0,
        )

    return ProfileResult(
        n_rows=int(df.shape[0]),
        n_cols=int(df.shape[1]),
        columns=columns,
    )
