"""sql-insights-agent command line.

Usage:
    python main.py demo
        # analyze data/sample_metrics.csv, print findings + insights,
        # write examples/sample_report.md

    python main.py analyze [--input data/sample_metrics.csv]
                           [--output examples/sample_report.md]
                           [--z-threshold 2.5]

Demo mode needs no API key and sends nothing: insights come from
deterministic templates and notifications are rendered as drafts only.
"""
import argparse
import os
import sys

from src.anomalies import detect_anomalies
from src.config import settings
from src.insights import generate_insights
from src.loader import load_metrics
from src.report import build_report, write_report
from src.trends import detect_trend_changes

DEFAULT_INPUT = "data/sample_metrics.csv"
DEFAULT_OUTPUT = "examples/sample_report.md"


def run_analysis(input_path: str, output_path: str, z_threshold: float):
    """Run the full pipeline and return (metrics, findings, trends, insights, report_path)."""
    metrics = load_metrics(input_path)
    findings = detect_anomalies(
        metrics,
        z_threshold=z_threshold,
        iqr_multiplier=settings.iqr_multiplier,
    )
    trends = detect_trend_changes(metrics)
    insights = generate_insights(findings, trends)
    report = build_report(
        metrics, findings, trends, insights, z_threshold, settings.iqr_multiplier
    )
    report_path = write_report(report, output_path)
    return metrics, findings, trends, insights, report_path


def print_results(metrics, findings, trends, insights) -> None:
    period = f"{metrics.dates[0]} to {metrics.dates[-1]}"
    print(f"sql-insights-agent — {metrics.n_days} days ({period})")
    print()
    print(f"Anomalies detected: {len(findings)}")
    for finding in findings:
        print(f"  {finding}")
    print()
    print(f"Trend changes: {len(trends)}")
    for change in trends:
        print(f"  {change}")
    print()
    print("Insights:")
    for insight in insights:
        print(f"  - {insight}")
    print()


def cmd_analyze(args) -> int:
    metrics, findings, trends, insights, report_path = run_analysis(
        args.input, args.output, args.z_threshold
    )
    print_results(metrics, findings, trends, insights)
    print(f"Report written to {report_path}")
    return 0


def cmd_demo(_args) -> int:
    print("Running demo on the synthetic sample data (no API key needed).")
    print()
    metrics, findings, trends, insights, report_path = run_analysis(
        DEFAULT_INPUT, DEFAULT_OUTPUT, settings.z_threshold
    )
    print_results(metrics, findings, trends, insights)
    print(f"Sample report written to {report_path}")
    print("Demo mode: insights are deterministic templates; no notifications were sent.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sql-insights-agent",
        description=(
            "Anomaly detection + plain-language insights over SQL query "
            "results (CSV). Demo mode needs no API key and sends nothing."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser(
        "demo",
        help="Analyze the bundled sample CSV and write examples/sample_report.md",
    )
    demo.set_defaults(func=cmd_demo)

    analyze = sub.add_parser(
        "analyze", help="Analyze a metrics CSV and write a markdown report"
    )
    analyze.add_argument(
        "--input",
        default=DEFAULT_INPUT,
        help=f"Input CSV file (default: {DEFAULT_INPUT})",
    )
    analyze.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Output markdown report (default: {DEFAULT_OUTPUT})",
    )
    analyze.add_argument(
        "--z-threshold",
        type=float,
        default=settings.z_threshold,
        help=f"z-score threshold for anomalies (default: {settings.z_threshold})",
    )
    analyze.set_defaults(func=cmd_analyze)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
