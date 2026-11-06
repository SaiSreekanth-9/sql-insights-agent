"""Anomaly detection over daily metrics.

Two complementary methods, run per numeric column:

* **z-score** — flag values with ``|z| >= z_threshold`` (default 2.5).
* **IQR rule** — flag values outside ``[Q1 - k*IQR, Q3 + k*IQR]``
  (default k = 1.5).

Both use only the stdlib (``statistics``), so detection works with no
third-party packages installed.
"""
import statistics
from dataclasses import dataclass

from .loader import NUMERIC_COLUMNS, Metrics


@dataclass
class Finding:
    """One detected anomaly."""

    date: str
    metric: str
    value: float
    method: str  # "z-score" or "iqr"
    score: float  # z-score, or distance outside the IQR fence in IQR units
    direction: str  # "high" or "low"
    mean: float
    stdev: float

    def __str__(self) -> str:
        return (
            f"{self.date} | {self.metric} = {self.value:g} "
            f"({self.method}, score {self.score:.2f}, {self.direction} "
            f"vs mean {self.mean:.2f})"
        )


def _zscore_findings(dates, values, metric, threshold):
    mean = statistics.fmean(values)
    stdev = statistics.pstdev(values)
    if stdev == 0:
        return []
    findings = []
    for date, value in zip(dates, values):
        z = (value - mean) / stdev
        if abs(z) >= threshold:
            findings.append(
                Finding(
                    date=date,
                    metric=metric,
                    value=value,
                    method="z-score",
                    score=z,
                    direction="high" if z > 0 else "low",
                    mean=mean,
                    stdev=stdev,
                )
            )
    return findings


def _iqr_findings(dates, values, metric, multiplier):
    quartiles = statistics.quantiles(values, n=4, method="inclusive")
    q1, q3 = quartiles[0], quartiles[2]
    iqr = q3 - q1
    if iqr == 0:
        return []
    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr
    mean = statistics.fmean(values)
    stdev = statistics.pstdev(values)
    findings = []
    for date, value in zip(dates, values):
        if value < lower or value > upper:
            # Score: how many IQRs beyond the fence the value sits.
            beyond = (value - upper) / iqr if value > upper else (lower - value) / iqr
            findings.append(
                Finding(
                    date=date,
                    metric=metric,
                    value=value,
                    method="iqr",
                    score=beyond,
                    direction="high" if value > upper else "low",
                    mean=mean,
                    stdev=stdev,
                )
            )
    return findings


def detect_anomalies(
    metrics: Metrics,
    z_threshold: float = 2.5,
    iqr_multiplier: float = 1.5,
    columns=None,
) -> list:
    """Run z-score and IQR detection over every numeric column.

    Returns findings sorted by date, then metric.
    """
    columns = columns or NUMERIC_COLUMNS
    findings: list = []
    for metric in columns:
        values = metrics.columns[metric]
        findings.extend(_zscore_findings(metrics.dates, values, metric, z_threshold))
        findings.extend(_iqr_findings(metrics.dates, values, metric, iqr_multiplier))
    findings.sort(key=lambda f: (f.date, f.metric, 0 if f.method == "z-score" else 1))
    return findings
