"""Data loading utilities for crime-analyzer."""

from pathlib import Path

import pandas as pd


def load_csv(csv_path: str) -> pd.DataFrame:
    """Load an incident CSV from a user-supplied path.

    Args:
        csv_path: Path to an exported CAD/incident CSV file.

    Returns:
        A pandas DataFrame with all source columns.

    Raises:
        FileNotFoundError: If the CSV path does not exist.
        ValueError: If the provided path is not a CSV file.
    """
    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(f"CSV file was not found: {path}")
    if path.suffix.lower() != ".csv":
        raise ValueError(f"Expected a .csv file, received: {path.name}")

    # dtype=str prevents pandas from aggressively type-casting source exports.
    # This keeps raw values intact for controlled cleaning/parsing later.
    return pd.read_csv(path, dtype=str)
