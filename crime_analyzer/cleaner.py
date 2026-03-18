"""Cleaning and normalization utilities for incident data."""

from __future__ import annotations

from typing import Iterable

import pandas as pd


# Canonical column names used by this project.
CANONICAL_COLUMNS = {
    "incident code": "incident_code",
    "incident_code": "incident_code",
    "code": "incident_code",
    "type": "incident_code",
    "incident type": "incident_code",
    "community": "community",
    "city": "community",
    "neighborhood": "community",
    "incident date": "incident_datetime_raw",
    "incident time": "incident_datetime_raw",
    "date": "incident_datetime_raw",
    "datetime": "incident_datetime_raw",
    "date time": "incident_datetime_raw",
    "occurred at": "incident_datetime_raw",
}

DATETIME_CANDIDATES = (
    "incident_datetime_raw",
    "incident_datetime",
    "date_time",
    "date",
    "incident_date",
    "occurred_at",
)



def _normalize_column_name(col: str) -> str:
    """Convert raw source column names into a consistent snake_case format."""
    normalized = col.strip().lower().replace("-", " ").replace("/", " ")
    normalized = "_".join(normalized.split())
    return CANONICAL_COLUMNS.get(normalized.replace("_", " "), normalized)



def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names and trim whitespace from object values."""
    cleaned = df.copy()

    cleaned.columns = [_normalize_column_name(col) for col in cleaned.columns]

    object_cols = cleaned.select_dtypes(include=["object"]).columns
    for col in object_cols:
        cleaned[col] = cleaned[col].astype(str).str.strip()
        cleaned[col] = cleaned[col].replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})

    return cleaned



def parse_incident_datetime(df: pd.DataFrame, candidates: Iterable[str] = DATETIME_CANDIDATES) -> pd.DataFrame:
    """Parse incident date/time into a normalized datetime column.

    Adds these derived columns:
      - incident_datetime
      - incident_month (YYYY-MM)
      - incident_day_of_week
      - incident_hour
    """
    parsed = df.copy()

    source_col = None
    for candidate in candidates:
        if candidate in parsed.columns:
            source_col = candidate
            break

    if source_col is None:
        raise KeyError(
            "Unable to find a date/time column. Add one of: "
            f"{', '.join(candidates)}"
        )

    parsed["incident_datetime"] = pd.to_datetime(
        parsed[source_col],
        errors="coerce",
        infer_datetime_format=True,
    )

    parsed["incident_month"] = parsed["incident_datetime"].dt.strftime("%Y-%m")
    parsed["incident_day_of_week"] = parsed["incident_datetime"].dt.day_name()
    parsed["incident_hour"] = parsed["incident_datetime"].dt.hour

    return parsed
