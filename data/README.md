# Sample data

`sample_metrics.csv` contains **synthetic, fictional daily metrics** for
30 days (2026-09-01 to 2026-09-30), generated with a seeded random script.
It stands in for the output of a SQL query against a metrics table.

Columns:

| Column | Meaning |
|---|---|
| `date` | Day (YYYY-MM-DD) |
| `active_users` | Daily active users |
| `revenue_usd` | Daily revenue in USD |
| `error_rate_pct` | Share of requests that errored, in percent |
| `avg_latency_ms` | Average request latency in milliseconds |

Planted patterns (so the demo has something real to find):

- **Revenue spike** on 2026-09-12 ($9,850 vs a ~$5,100 average)
- **Error-rate spike** on 2026-09-18 (4.90% vs a ~1.0% average)
- **Latency spike** on 2026-09-25 (640 ms vs a ~200 ms average)
- **Step change in active users** around 2026-09-20 (from ~1,050/day to
  ~1,520/day — a sustained level shift, not a one-day anomaly)

None of these numbers come from any real company, product, or production
system.
