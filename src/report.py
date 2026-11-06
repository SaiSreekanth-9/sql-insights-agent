"""Markdown report builder: findings + trends + insights + drafts -> file."""
import os

from .anomalies import Finding
from .loader import Metrics
from .notify import render_draft_email, render_slack_message
from .trends import TrendChange

DATA_NOTE = (
    "All values in this report are synthetic sample data, generated for "
    "demonstration purposes. They do not come from any real company, "
    "product, or production system."
)


def build_report(
    metrics: Metrics,
    findings: list,
    trends: list,
    insights: list,
    z_threshold: float,
    iqr_multiplier: float,
) -> str:
    """Render the full markdown report as a string."""
    period = f"{metrics.dates[0]} to {metrics.dates[-1]}"
    lines = [
        "# SQL Insights Report",
        "",
        f"**Period:** {period} ({metrics.n_days} days)",
        f"**Detection:** z-score |z| ≥ {z_threshold}, IQR rule "
        f"({iqr_multiplier}×IQR)",
        "",
        "> " + DATA_NOTE,
        "",
        "## Data summary",
        "",
        "| Metric | Min | Mean | Max |",
        "|---|---|---|---|",
    ]
    for metric, values in metrics.columns.items():
        lines.append(
            f"| {metric} | {min(values):g} | {sum(values) / len(values):.2f} "
            f"| {max(values):g} |"
        )
    lines += ["", "## Anomalies detected", ""]
    if findings:
        lines += [
            "| Date | Metric | Value | Method | Score | Direction |",
            "|---|---|---|---|---|---|",
        ]
        for f in findings:
            lines.append(
                f"| {f.date} | {f.metric} | {f.value:g} | {f.method} | "
                f"{f.score:.2f} | {f.direction} |"
            )
    else:
        lines.append("No anomalies detected.")
    lines += ["", "## Trend changes", ""]
    if trends:
        for change in trends:
            lines.append(f"- {change}")
    else:
        lines.append("No trend changes detected.")
    lines += ["", "## Insights", ""]
    for insight in insights:
        lines.append(f"- {insight}")
    email = render_draft_email(insights, period)
    lines += [
        "",
        "## Notification drafts (not sent)",
        "",
        "### Email draft",
        "",
        f"**Subject:** {email['subject']}",
        "",
        "```",
        email["body"],
        "```",
        "",
        "### Slack draft",
        "",
        "```",
        render_slack_message(insights, period),
        "```",
        "",
        "---",
        "",
        DATA_NOTE,
        "",
    ]
    return "\n".join(lines)


def write_report(report: str, output_path: str) -> str:
    """Write ``report`` to ``output_path`` (creating parent dirs) and return the path."""
    parent = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(parent, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report)
    return output_path
