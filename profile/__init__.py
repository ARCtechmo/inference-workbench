"""profile: Level 2 data profiling — surface issues, do not fix.

Inspects a loaded DataFrame and reports missingness, structural type
proposals, near-constant and high-cardinality columns, and outliers.
Analytical classification (ordinal/nominal, roles) is the workflow's job.
"""

from .checks import (
    check_missingness,
    count_outliers,
    count_unique,
    is_high_cardinality,
    is_near_constant,
    profile,
    propose_type,
)
from .schema import ColumnProfile, ProfileResult

__all__ = [
    "ColumnProfile",
    "ProfileResult",
    "check_missingness",
    "count_outliers",
    "count_unique",
    "is_high_cardinality",
    "is_near_constant",
    "profile",
    "propose_type",
]
