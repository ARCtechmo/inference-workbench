"""Unit tests for the profile layer.

Each profile check is tested in isolation, plus the orchestrator and the
flagged_columns triage helper. Tests assert that the layer *surfaces*
findings correctly — they do not test any fixing behavior, because the
layer does not fix.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from profile import (
    ProfileResult,
    check_missingness,
    count_outliers,
    count_unique,
    is_high_cardinality,
    is_near_constant,
    profile,
    propose_type,
)


# --- check_missingness ---

def test_missingness_none():
    s = pd.Series([1, 2, 3])
    assert check_missingness(s) == (0, 0.0)


def test_missingness_some():
    s = pd.Series([1, None, 3, None])
    n, pct = check_missingness(s)
    assert n == 2
    assert pct == 0.5


def test_missingness_empty_series():
    s = pd.Series([], dtype="float64")
    assert check_missingness(s) == (0, 0.0)


# --- count_unique ---

def test_count_unique_ignores_nulls():
    s = pd.Series([1, 1, 2, None])
    assert count_unique(s) == 2


# --- propose_type ---

def test_propose_empty():
    s = pd.Series([None, None], dtype="object")
    assert propose_type(s) == "empty"


def test_propose_binary_numeric():
    s = pd.Series([0, 1, 1, 0, 1])
    assert propose_type(s) == "binary"


def test_propose_binary_string():
    s = pd.Series(["yes", "no", "yes"])
    assert propose_type(s) == "binary"


def test_propose_continuous_float():
    s = pd.Series([1.1, 2.2, 3.3, 4.4])
    assert propose_type(s) == "continuous"


def test_propose_count_small_nonneg_int():
    s = pd.Series([0, 1, 2, 3, 4, 5])
    assert propose_type(s) == "count"


def test_propose_continuous_large_range_int():
    s = pd.Series([10, 5000, 99999, 250000])
    assert propose_type(s) == "continuous"


def test_propose_continuous_negative_int():
    # Negative values rule out "count" -> continuous
    s = pd.Series([-5, 0, 3, 10, 22])
    assert propose_type(s) == "continuous"


def test_propose_categorical_string():
    s = pd.Series(["a", "b", "c", "d"])
    assert propose_type(s) == "categorical"


def test_binary_beats_count():
    # 0/1 ints are binary, not count
    s = pd.Series([0, 1, 0, 1, 1, 0])
    assert propose_type(s) == "binary"


# --- is_near_constant ---

def test_near_constant_true():
    s = pd.Series([1] * 96 + [2] * 4)
    assert is_near_constant(s) is True


def test_near_constant_false():
    s = pd.Series([1] * 50 + [2] * 50)
    assert is_near_constant(s) is False


def test_near_constant_ignores_nulls():
    s = pd.Series([1] * 96 + [2] * 4 + [None] * 20)
    assert is_near_constant(s) is True


# --- is_high_cardinality ---

def test_high_cardinality_absolute():
    s = pd.Series([f"id_{i}" for i in range(60)])
    assert is_high_cardinality(s) is True


def test_high_cardinality_relative_id_like():
    # 6 unique in 10 rows -> 0.6 > 0.5 relative threshold
    s = pd.Series(["a", "b", "c", "d", "e", "f", "a", "b", "c", "d"])
    assert is_high_cardinality(s) is True


def test_high_cardinality_low():
    s = pd.Series(["red", "green", "blue"] * 20)
    assert is_high_cardinality(s) is False


def test_high_cardinality_numeric_is_false():
    # Numeric columns are never high-cardinality (not meaningful)
    s = pd.Series(range(1000))
    assert is_high_cardinality(s) is False


# --- count_outliers ---

def test_outliers_none():
    s = pd.Series([10, 11, 12, 13, 14, 15])
    assert count_outliers(s) == 0


def test_outliers_detected():
    s = pd.Series([10, 11, 12, 13, 14, 15, 1000])
    assert count_outliers(s) >= 1


def test_outliers_non_numeric_is_zero():
    s = pd.Series(["a", "b", "c"])
    assert count_outliers(s) == 0


def test_outliers_zero_iqr():
    # All identical -> IQR 0 -> no outliers (avoids div-by-zero nonsense)
    s = pd.Series([5, 5, 5, 5, 5])
    assert count_outliers(s) == 0


# --- profile orchestrator ---

def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "age": [25, 34, 45, 28, 52, 31],
            "hired": [1, 0, 1, 0, 1, 0],
            "dept": ["eng", "sales", "eng", "hr", "sales", "eng"],
            "salary": [50000.0, 60000.0, 75000.0, 48000.0, 999999.0, 55000.0],
            "notes": [None, None, None, None, None, None],
        }
    )


def test_profile_returns_result():
    result = profile(_sample_df())
    assert isinstance(result, ProfileResult)
    assert result.n_rows == 6
    assert result.n_cols == 5
    assert set(result.columns.keys()) == {"age", "hired", "dept", "salary", "notes"}


def test_profile_proposed_types():
    cols = profile(_sample_df()).columns
    assert cols["hired"].proposed_type == "binary"
    assert cols["dept"].proposed_type == "categorical"
    assert cols["salary"].proposed_type == "continuous"
    assert cols["notes"].proposed_type == "empty"
    # age: non-neg int, range 27 (<=100) -> count
    assert cols["age"].proposed_type == "count"


def test_profile_outliers_only_continuous():
    cols = profile(_sample_df()).columns
    # salary has an extreme value -> continuous -> outliers counted
    assert cols["salary"].n_outliers >= 1
    # hired is binary -> outliers forced to 0 even though numeric
    assert cols["hired"].n_outliers == 0


def test_profile_missing_surfaced():
    cols = profile(_sample_df()).columns
    assert cols["notes"].n_missing == 6
    assert cols["notes"].pct_missing == 1.0


def test_flagged_columns():
    flagged = profile(_sample_df()).flagged_columns()
    # notes (empty+missing) and salary (outlier) should be flagged
    assert "notes" in flagged
    assert "salary" in flagged
    # hired (clean binary) should not be flagged
    assert "hired" not in flagged
