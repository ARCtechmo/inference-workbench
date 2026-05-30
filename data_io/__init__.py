"""data_io: the only layer that reads or writes data files.

Returns typed pandas DataFrames (native inference) plus observed-fact
metadata. Does not clean, transform, or make analytical type judgments.
"""

from .exceptions import DataLoadError
from .loader import load_csv, load_excel, load_parquet
from .metadata import DatasetMetadata

__all__ = [
    "DataLoadError",
    "DatasetMetadata",
    "load_csv",
    "load_excel",
    "load_parquet",
]
