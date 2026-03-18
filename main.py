"""CLI entrypoint for the crime-analyzer application."""

from __future__ import annotations

import argparse

from crime_analyzer.pipeline import run_analysis


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="crime-analyzer",
        description="Analyze sheriff CAD/incident CSV exports and generate charts + report.",
    )
    parser.add_argument("csv_path", help="Path to input CSV export")
    parser.add_argument(
        "--config",
        default="config/incident_group_mappings.json",
        help="Path to JSON config containing incident group mappings",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Directory where report/charts will be written",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_analysis(args.csv_path, args.output_dir, args.config)

    print(f"Analysis complete. Outputs written to: {result['output_dir'].resolve()}")
    print(f"Report: {result['report_path'].resolve()}")


if __name__ == "__main__":
    main()
