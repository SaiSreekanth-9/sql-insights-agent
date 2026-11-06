"""Load daily metrics from a CSV file (the stand-in for SQL query output).

Uses pandas when it is installed, otherwise falls back to the stdlib
``csv`` module, so the core pipeline works anywhere.
"""
import csv
import os
from dataclasses import dataclass, field

NUMERIC_COLUMNS = ["active_users", "revenue_usd", "error_rate_pct", "avg_latency_ms"]


@dataclass
class Metrics:
    """One column of daily values, plus the shared date index."""

    dates: list
    columns: dict = field(default_factory=dict)

    @property
    def n_days(self) -> int:
        return len(self.dates)


def _load_with_csv(path: str) -> Metrics:
    dates: list = []
    columns: dict = {col: [] for col in NUMERIC_COLUMNS}
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dates.append(row["date"])
            for col in NUMERIC_COLUMNS:
                columns[col].append(float(row[col]))
    return Metrics(dates=dates, columns=columns)


def _load_with_pandas(path: str) -> Metrics:
    import pandas as pd

    df = pd.read_csv(path)
    dates = [str(d) for d in df["date"]]
    columns = {col: [float(v) for v in df[col]] for col in NUMERIC_COLUMNS}
    return Metrics(dates=dates, columns=columns)


def load_metrics(path: str) -> Metrics:
    """Read ``path`` into a :class:`Metrics` object.

    Prefers pandas when available; falls back to the stdlib csv module.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Metrics file not found: {path}")
    try:
        import pandas  # noqa: F401  (optional dependency)
    except ImportError:
        return _load_with_csv(path)
    return _load_with_pandas(path)
