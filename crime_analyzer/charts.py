"""Chart rendering for crime-analyzer outputs."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd



def _save_bar_chart(series: pd.Series, title: str, xlabel: str, ylabel: str, out_path: Path) -> None:
    """Render and save a standard bar chart from a pandas Series."""
    plt.figure(figsize=(10, 6))
    series.plot(kind="bar", color="#2f5597")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()



def create_charts(summary_tables: dict[str, pd.Series], output_dir: Path) -> dict[str, Path]:
    """Create all requested charts and return their file paths."""
    output_dir.mkdir(parents=True, exist_ok=True)
    chart_paths: dict[str, Path] = {}

    if not summary_tables["by_month"].empty:
        month_series = summary_tables["by_month"].sort_index()
        out = output_dir / "incidents_by_month.png"
        _save_bar_chart(month_series, "Incidents by Month", "Month", "Incident Count", out)
        chart_paths["incidents_by_month"] = out

    if not summary_tables["by_hour"].empty:
        hour_series = summary_tables["by_hour"].sort_index()
        out = output_dir / "incidents_by_hour.png"
        _save_bar_chart(hour_series, "Incidents by Hour", "Hour of Day", "Incident Count", out)
        chart_paths["incidents_by_hour"] = out

    if not summary_tables["by_day_of_week"].empty:
        weekday_order = [
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
        ]
        day_series = summary_tables["by_day_of_week"].reindex(weekday_order).dropna()
        out = output_dir / "incidents_by_day_of_week.png"
        _save_bar_chart(day_series, "Incidents by Day of Week", "Day", "Incident Count", out)
        chart_paths["incidents_by_day_of_week"] = out

    if not summary_tables["by_community"].empty:
        community_series = summary_tables["by_community"].head(10)
        out = output_dir / "top_10_communities.png"
        _save_bar_chart(community_series, "Top 10 Communities by Incident Count", "Community", "Incident Count", out)
        chart_paths["top_10_communities"] = out

    if not summary_tables["by_incident_code"].empty:
        incident_series = summary_tables["by_incident_code"].head(10)
        out = output_dir / "top_10_incident_types.png"
        _save_bar_chart(incident_series, "Top 10 Incident Types", "Incident Type", "Incident Count", out)
        chart_paths["top_10_incident_types"] = out

    return chart_paths
