"""Analytical aggregations for incident datasets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import pandas as pd



def load_group_mapping(config_path: str | None) -> Dict[str, list[str]]:
    """Load optional incident grouping config from a JSON file."""
    if not config_path:
        return {}

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Mapping config not found: {path}")

    with path.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)

    return payload.get("incident_groups", {})



def apply_incident_groups(df: pd.DataFrame, group_map: Dict[str, list[str]]) -> pd.DataFrame:
    """Create an `incident_group` column using configurable code groupings."""
    enriched = df.copy()

    if "incident_code" not in enriched.columns:
        enriched["incident_group"] = "Unmapped"
        return enriched

    reverse_lookup = {}
    for group_name, codes in group_map.items():
        for code in codes:
            reverse_lookup[str(code).strip().lower()] = group_name

    enriched["incident_group"] = (
        enriched["incident_code"]
        .fillna("Unmapped")
        .astype(str)
        .str.strip()
        .str.lower()
        .map(reverse_lookup)
        .fillna("Unmapped")
    )

    return enriched



def count_by_column(df: pd.DataFrame, column: str) -> pd.Series:
    """Count incidents for a given column."""
    if column not in df.columns:
        raise KeyError(f"Column '{column}' not found in dataset")

    return (
        df[column]
        .dropna()
        .value_counts()
        .sort_values(ascending=False)
    )



def build_summary_tables(df: pd.DataFrame) -> dict[str, pd.Series]:
    """Generate all required aggregate tables for reporting and charts."""
    tables = {
        "by_incident_code": count_by_column(df, "incident_code") if "incident_code" in df.columns else pd.Series(dtype="int64"),
        "by_community": count_by_column(df, "community") if "community" in df.columns else pd.Series(dtype="int64"),
        "by_month": count_by_column(df, "incident_month") if "incident_month" in df.columns else pd.Series(dtype="int64"),
        "by_day_of_week": count_by_column(df, "incident_day_of_week") if "incident_day_of_week" in df.columns else pd.Series(dtype="int64"),
        "by_hour": count_by_column(df, "incident_hour") if "incident_hour" in df.columns else pd.Series(dtype="int64"),
        "by_incident_group": count_by_column(df, "incident_group") if "incident_group" in df.columns else pd.Series(dtype="int64"),
    }

    return tables
