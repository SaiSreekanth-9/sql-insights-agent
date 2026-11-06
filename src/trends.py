"""Trend-change detection: level shifts between two halves of the series.

For each numeric column, compare the median of the first half of the window
with the median of the second half and report the direction and percent
change. Medians (not means) are used so that a single-day spike does not
masquerade as a sustained trend — a real step change shows up here even
when no single day is anomalous enough for z-score / IQR detection.
"""
import statistics
from dataclasses import dataclass

from .loader import NUMERIC_COLUMNS, Metrics


@dataclass
class TrendChange:
    """One detected level shift between the two halves of the series."""

    metric: str
    first_half_median: float
    second_half_median: float
    pct_change: float  # second half vs first half, in percent
    direction: str  # "up" or "down"
    split_date: str  # first date of the second half

    def __str__(self) -> str:
        return (
            f"{self.metric}: {self.direction} {abs(self.pct_change):.1f}% "
            f"({self.first_half_median:.2f} -> {self.second_half_median:.2f} median, "
            f"split at {self.split_date})"
        )


def detect_trend_changes(
    metrics: Metrics,
    min_pct_change: float = 10.0,
    columns=None,
) -> list:
    """Compare first-half vs second-half medians per column.

    Only shifts of at least ``min_pct_change`` percent are reported, so
    ordinary noise does not surface as a "trend change".
    """
    columns = columns or NUMERIC_COLUMNS
    n = metrics.n_days
    if n < 4:
        return []
    split = n // 2
    split_date = metrics.dates[split]
    changes: list = []
    for metric in columns:
        values = metrics.columns[metric]
        first = statistics.median(values[:split])
        second = statistics.median(values[split:])
        if first == 0:
            continue
        pct = (second - first) / abs(first) * 100
        if abs(pct) >= min_pct_change:
            changes.append(
                TrendChange(
                    metric=metric,
                    first_half_median=first,
                    second_half_median=second,
                    pct_change=pct,
                    direction="up" if pct > 0 else "down",
                    split_date=split_date,
                )
            )
    changes.sort(key=lambda c: -abs(c.pct_change))
    return changes
