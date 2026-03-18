"""Shared orchestration pipeline for CLI and GUI flows."""

from __future__ import annotations

from pathlib import Path

from crime_analyzer.analysis import apply_incident_groups, build_summary_tables, load_group_mapping
from crime_analyzer.charts import create_charts
from crime_analyzer.cleaner import parse_incident_datetime, standardize_columns
from crime_analyzer.loader import load_csv
from crime_analyzer.report import write_markdown_report


def run_analysis(csv_path: str, output_dir: str, config_path: str | None = None) -> dict[str, object]:
    """Run complete incident analysis pipeline and return output metadata."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    raw_df = load_csv(csv_path)
    cleaned_df = standardize_columns(raw_df)
    parsed_df = parse_incident_datetime(cleaned_df)

    group_map = load_group_mapping(config_path)
    enriched_df = apply_incident_groups(parsed_df, group_map)

    summary_tables = build_summary_tables(enriched_df)
    chart_paths = create_charts(summary_tables, output_path)
    report_path = write_markdown_report(summary_tables, output_path, chart_paths)

    return {
        "output_dir": output_path,
        "report_path": report_path,
        "chart_paths": chart_paths,
        "summary_tables": summary_tables,
    }
