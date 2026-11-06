"""Plain-language insights generated from findings and trend changes.

Demo mode uses deterministic templates — no API key, no model call, fully
reproducible. When ``OPENAI_API_KEY`` is set, :func:`rewrite_with_llm`
optionally rewrites the template sentences with an LLM; the import of
langchain is lazy, inside that function, so the module works fine without
langchain installed.
"""
from .anomalies import Finding
from .config import settings
from .trends import TrendChange

# Human-friendly labels and units for the metric columns.
METRIC_LABELS = {
    "active_users": ("active users", ""),
    "revenue_usd": ("revenue", " USD"),
    "error_rate_pct": ("error rate", "%"),
    "avg_latency_ms": ("average latency", " ms"),
}


def _format_value(metric: str, value: float) -> str:
    label, unit = METRIC_LABELS.get(metric, (metric, ""))
    if metric == "revenue_usd":
        return f"${value:,.0f}"
    if metric == "error_rate_pct":
        return f"{value:.2f}%"
    if metric == "avg_latency_ms":
        return f"{value:.0f} ms"
    return f"{value:,.0f}{unit}"


def insight_for_finding(finding: Finding) -> str:
    """One deterministic sentence for a single anomaly finding."""
    label, _ = METRIC_LABELS.get(finding.metric, (finding.metric, ""))
    value = _format_value(finding.metric, finding.value)
    mean = _format_value(finding.metric, finding.mean)
    direction = "spiked to" if finding.direction == "high" else "dropped to"
    return (
        f"On {finding.date}, {label} {direction} {value} — well "
        f"{'above' if finding.direction == 'high' else 'below'} the "
        f"30-day average of {mean} "
        f"({finding.method} score {finding.score:.2f})."
    )


def insight_for_trend(change: TrendChange) -> str:
    """One deterministic sentence for a detected level shift."""
    label, _ = METRIC_LABELS.get(change.metric, (change.metric, ""))
    before = _format_value(change.metric, change.first_half_median)
    after = _format_value(change.metric, change.second_half_median)
    return (
        f"{label.capitalize()} shifted {change.direction} by "
        f"{abs(change.pct_change):.1f}% between the first and second half "
        f"of the period ({before} → {after} median, split "
        f"{change.split_date}) — a sustained level change, not a one-day blip."
    )


def generate_insights(findings: list, trends: list) -> list:
    """Build the full insight list from findings + trend changes.

    De-duplicates: a metric flagged by both z-score and IQR on the same day
    produces a single insight (the z-score one, which carries the score).
    """
    insights: list = []
    seen: set = set()
    for finding in findings:
        key = (finding.date, finding.metric)
        if key in seen:
            continue
        seen.add(key)
        insights.append(insight_for_finding(finding))
    for change in trends:
        insights.append(insight_for_trend(change))
    if not insights:
        insights.append(
            "No anomalies or trend changes detected in this period — "
            "all metrics stayed within their normal range."
        )
    return insights


def rewrite_with_llm(insights: list) -> list:
    """Optionally rewrite template insights with an LLM (gpt-4o-mini).

    Requires ``OPENAI_API_KEY``. langchain is imported lazily here and is
    never needed for the default template path. Raises RuntimeError with a
    clear message when the key is missing.
    """
    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Leave it unset for deterministic "
            "template insights, or copy .env.example to .env and add your key "
            "to enable the LLM rewrite."
        )
    from langchain_openai import ChatOpenAI  # lazy import — optional dep

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = (
        "Rewrite each of the following data insights as a single concise, "
        "plain-language sentence for a non-technical stakeholder. Keep every "
        "number and date exactly as given; do not add new facts.\n\n"
        + "\n".join(f"- {insight}" for insight in insights)
    )
    response = llm.invoke(prompt)
    rewritten = [
        line.lstrip("- ").strip()
        for line in response.content.splitlines()
        if line.strip()
    ]
    return rewritten or insights
