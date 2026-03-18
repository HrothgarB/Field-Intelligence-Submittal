# crime-analyzer

`crime-analyzer` is a Python application for analyzing sheriff's office CAD or incident CSV exports.

## Features
- Load incident CSV files from a user-provided path (CLI) or file upload (GUI).
- Browser-accessible GUI with an **initial setup flow** to capture runtime variables:
  - input file type
  - output path
  - incident file import
  - optional config file import
- Standardize columns and trim whitespace.
- Parse incident date/time fields into usable datetime values.
- Group and summarize incidents by:
  - incident code
  - community
  - month
  - day of week
  - hour of day
- Generate charts for:
  - incidents by month
  - incidents by hour
  - incidents by day of week
  - top 10 communities
  - top 10 incident types
- Save outputs into an `outputs/` folder (or user-selected output path).
- Generate a markdown summary report that includes a **Key Findings** section.
- Modular architecture (`loader`, `cleaner`, `analysis`, `charts`, `report`, `pipeline`) to keep code maintainable.
- Includes a sample group mapping config file that can be expanded with categories like property crime, violent crime, suspicious activity, traffic stops, and proactive activity.

## Project Structure

```text
crime_analyzer/
  loader.py
  cleaner.py
  analysis.py
  charts.py
  report.py
  pipeline.py
main.py
webapp.py
config/incident_group_mappings.json
outputs/
```

## Detailed Installation Instructions

### 1) Clone the repository

```bash
git clone <YOUR_REPO_URL>
cd Field-Intelligence-Submittal
```

### 2) Confirm Python version
Python 3.10+ is recommended.

```bash
python --version
```

### 3) Create and activate a virtual environment

**macOS/Linux**
```bash
python -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 4) Upgrade pip tooling (recommended)

```bash
python -m pip install --upgrade pip setuptools wheel
```

### 5) Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 6) Verify install (optional but recommended)

```bash
python -m py_compile main.py webapp.py crime_analyzer/*.py
```

## Usage

### CLI

```bash
python main.py /path/to/incidents.csv \
  --config config/incident_group_mappings.json \
  --output-dir outputs
```

### Browser GUI

```bash
python webapp.py
```

Then open: `http://localhost:5000`

The initial setup screen prompts for file type, output path, and file imports before running analysis.

## Expected Input Fields
The app attempts to normalize several common field names from CAD exports. For best results include at least:
- incident code/type (for incident type summaries)
- community/city/neighborhood
- incident date/time

## Outputs
The output directory includes:
- `summary_report.md`
- `incidents_by_month.png`
- `incidents_by_hour.png`
- `incidents_by_day_of_week.png`
- `top_10_communities.png`
- `top_10_incident_types.png`

## Troubleshooting
- If `pip install -r requirements.txt` fails in a restricted network, configure your organization proxy/index and retry.
- If `python webapp.py` fails with missing `flask`, ensure dependencies installed successfully in the active virtual environment.
- If charts or report are missing, confirm input CSV contains parseable incident date/time and incident type/community fields.
