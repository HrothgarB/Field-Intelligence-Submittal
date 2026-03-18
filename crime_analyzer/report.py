"""Markdown report generation for crime-analyzer."""

from pathlib import Path

import pandas as pd



def _series_to_markdown(series: pd.Series, top_n: int | None = None) -> str:
    if series.empty:
        return "_No data available._"

    data = series.head(top_n) if top_n else series
    rows = ["| Value | Count |", "|---|---:|"]
    rows.extend([f"| {idx} | {val} |" for idx, val in data.items()])
    return "\n".join(rows)



def write_markdown_report(
    summary_tables: dict[str, pd.Series],
    output_dir: Path,
    chart_paths: dict[str, Path],
) -> Path:
    """Write a markdown summary report with required key findings section."""
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "summary_report.md"

    total_incidents = int(summary_tables["by_incident_code"].sum()) if not summary_tables["by_incident_code"].empty else 0

    top_type = summary_tables["by_incident_code"].index[0] if not summary_tables["by_incident_code"].empty else "N/A"
    top_community = summary_tables["by_community"].index[0] if not summary_tables["by_community"].empty else "N/A"
    peak_hour = summary_tables["by_hour"].index[0] if not summary_tables["by_hour"].empty else "N/A"

    content = [
        "# Crime Analyzer Summary Report",
        "",
        "## Overview",
        f"- Total incidents analyzed: **{total_incidents}**",
        f"- Distinct incident types: **{len(summary_tables['by_incident_code'])}**",
        f"- Distinct communities: **{len(summary_tables['by_community'])}**",
        "",
        "## Key Findings",
        f"- Most frequent incident type: **{top_type}**",
        f"- Most impacted community: **{top_community}**",
        f"- Peak incident hour: **{peak_hour}**",
        "",
        "## Incidents by Month",
        _series_to_markdown(summary_tables["by_month"]),
        "",
        "## Incidents by Hour",
        _series_to_markdown(summary_tables["by_hour"]),
        "",
        "## Incidents by Day of Week",
        _series_to_markdown(summary_tables["by_day_of_week"]),
        "",
        "## Top 10 Communities",
        _series_to_markdown(summary_tables["by_community"], top_n=10),
        "",
        "## Top 10 Incident Types",
        _series_to_markdown(summary_tables["by_incident_code"], top_n=10),
        "",
        "## Generated Charts",
    ]

    for name, path in chart_paths.items():
        content.append(f"- {name}: `{path.name}`")

    report_path.write_text("\n".join(content), encoding="utf-8")
    return report_path
