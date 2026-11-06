# Sample outputs

> Generated with `python main.py demo` (no API key, no network calls).
> All data is synthetic — see `data/README.md` for the planted patterns.
> The full generated report is in [sample_report.md](sample_report.md).

## `python main.py demo`

```
Running demo on the synthetic sample data (no API key needed).

sql-insights-agent — 30 days (2026-09-01 to 2026-09-30)

Anomalies detected: 6
  2026-09-12 | revenue_usd = 9850 (z-score, score 5.28, high vs mean 5251.43)
  2026-09-12 | revenue_usd = 9850 (iqr, score 19.15, high vs mean 5251.43)
  2026-09-18 | error_rate_pct = 4.9 (z-score, score 5.30, high vs mean 1.15)
  2026-09-18 | error_rate_pct = 4.9 (iqr, score 18.96, high vs mean 1.15)
  2026-09-25 | avg_latency_ms = 640 (z-score, score 5.34, high vs mean 215.07)
  2026-09-25 | avg_latency_ms = 640 (iqr, score 22.46, high vs mean 215.07)

Trend changes: 1
  active_users: up 41.6% (1059.00 -> 1500.00 median, split at 2026-09-16)

Insights:
  - On 2026-09-12, revenue spiked to $9,850 — well above the 30-day average of $5,251 (z-score score 5.28).
  - On 2026-09-18, error rate spiked to 4.90% — well above the 30-day average of 1.15% (z-score score 5.30).
  - On 2026-09-25, average latency spiked to 640 ms — well above the 30-day average of 215 ms (z-score score 5.34).
  - Active users shifted up by 41.6% between the first and second half of the period (1,059 → 1,500 median, split 2026-09-16) — a sustained level change, not a one-day blip.

Sample report written to examples/sample_report.md
Demo mode: insights are deterministic templates; no notifications were sent.
```

## What the demo found

Every planted pattern in `data/sample_metrics.csv` was detected:

| Planted pattern | Detected as |
|---|---|
| Revenue spike, 2026-09-12 ($9,850) | z-score 5.28 **and** IQR 19.15 |
| Error-rate spike, 2026-09-18 (4.90%) | z-score 5.30 **and** IQR 18.96 |
| Latency spike, 2026-09-25 (640 ms) | z-score 5.34 **and** IQR 22.46 |
| Active-users step change ~2026-09-20 | Trend change: up 41.6% (median 1,059 → 1,500) |

Note the trend detector uses medians, so the one-day error-rate and latency
spikes did **not** surface as false trend changes — only the genuine,
sustained active-users level shift did.
