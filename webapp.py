"""Browser-accessible GUI for crime-analyzer."""

from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4

from flask import Flask, abort, redirect, render_template_string, request, send_file, url_for
from werkzeug.utils import secure_filename

from crime_analyzer.pipeline import run_analysis

app = Flask(__name__)
RUN_RESULTS: dict[str, dict[str, str]] = {}

SETUP_TEMPLATE = """
<!doctype html>
<html>
  <head>
    <title>crime-analyzer setup</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 2rem auto; max-width: 900px; }
      .card { border: 1px solid #ddd; border-radius: 8px; padding: 1rem 1.25rem; }
      .row { margin-bottom: 0.75rem; }
      label { font-weight: 600; display: block; margin-bottom: 0.25rem; }
      input, select { width: 100%; padding: 0.45rem; }
      .error { color: #b00020; }
      button { padding: 0.55rem 1rem; }
    </style>
  </head>
  <body>
    <h1>crime-analyzer</h1>
    <p>Initial setup: choose input/output variables and import files.</p>
    <div class="card">
      {% if error %}<p class="error">{{ error }}</p>{% endif %}
      <form method="post" enctype="multipart/form-data" action="{{ url_for('run_setup') }}">
        <div class="row">
          <label for="filetype">Input file type</label>
          <select name="filetype" id="filetype">
            <option value="csv" selected>CSV</option>
          </select>
        </div>
        <div class="row">
          <label for="output_dir">Output directory path</label>
          <input type="text" id="output_dir" name="output_dir" value="outputs" required>
        </div>
        <div class="row">
          <label for="incident_file">Incident file import</label>
          <input type="file" id="incident_file" name="incident_file" accept=".csv" required>
        </div>
        <div class="row">
          <label for="config_file">Optional mapping config import (JSON)</label>
          <input type="file" id="config_file" name="config_file" accept=".json">
        </div>
        <button type="submit">Run Analysis</button>
      </form>
    </div>
  </body>
</html>
"""

RESULT_TEMPLATE = """
<!doctype html>
<html>
  <head>
    <title>crime-analyzer results</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 2rem auto; max-width: 900px; }
      .charts img { width: 100%; max-width: 780px; margin-bottom: 1rem; border: 1px solid #ddd; }
      ul { line-height: 1.6; }
      .chip { display: inline-block; background: #eef5ff; border: 1px solid #cddfff; border-radius: 999px; padding: .15rem .6rem; }
    </style>
  </head>
  <body>
    <h1>Analysis Complete</h1>
    <p><span class="chip">Output folder:</span> <code>{{ output_dir }}</code></p>
    <ul>
      <li>Report: <a href="{{ url_for('download_output', run_id=run_id, kind='report', name=report_name) }}">{{ report_name }}</a></li>
      {% for chart in charts %}
      <li>Chart: <a href="{{ url_for('download_output', run_id=run_id, kind='chart', name=chart) }}">{{ chart }}</a></li>
      {% endfor %}
    </ul>

    <h2>Chart Preview</h2>
    <div class="charts">
      {% for chart in charts %}
      <img src="{{ url_for('download_output', run_id=run_id, kind='chart', name=chart) }}" alt="{{ chart }}">
      {% endfor %}
    </div>

    <p><a href="{{ url_for('index') }}">Run another analysis</a></p>
  </body>
</html>
"""


@app.get("/")
def index():
    return render_template_string(SETUP_TEMPLATE, error=None)


@app.post("/run")
def run_setup():
    try:
        filetype = request.form.get("filetype", "csv").lower().strip()
        output_dir = request.form.get("output_dir", "outputs").strip() or "outputs"
        incident_file = request.files.get("incident_file")
        config_file = request.files.get("config_file")

        if filetype != "csv":
            raise ValueError("Only CSV is currently supported.")
        if incident_file is None or incident_file.filename == "":
            raise ValueError("Incident CSV file is required.")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        incident_name = secure_filename(incident_file.filename) or "input.csv"
        incident_path = output_path / incident_name
        incident_file.save(incident_path)

        config_path = "config/incident_group_mappings.json"
        if config_file is not None and config_file.filename:
            with NamedTemporaryFile(delete=False, suffix=".json", dir=output_path) as tmp:
                config_file.save(tmp.name)
                config_path = tmp.name

        result = run_analysis(str(incident_path), str(output_path), config_path)

        run_id = uuid4().hex
        RUN_RESULTS[run_id] = {
            "output_dir": str(result["output_dir"].resolve()),
            "report": str(result["report_path"].resolve()),
            "charts": [str(path.resolve()) for path in result["chart_paths"].values()],
        }

        return redirect(url_for("results", run_id=run_id))
    except Exception as exc:
        return render_template_string(SETUP_TEMPLATE, error=str(exc)), 400


@app.get("/results/<run_id>")
def results(run_id: str):
    run = RUN_RESULTS.get(run_id)
    if not run:
        return redirect(url_for("index"))

    chart_names = [Path(path).name for path in run["charts"]]
    return render_template_string(
        RESULT_TEMPLATE,
        run_id=run_id,
        output_dir=run["output_dir"],
        report_name=Path(run["report"]).name,
        charts=chart_names,
    )


@app.get("/download/<run_id>/<kind>/<name>")
def download_output(run_id: str, kind: str, name: str):
    run = RUN_RESULTS.get(run_id)
    if not run:
        abort(404)

    if kind == "report":
        report = Path(run["report"])
        if report.name != name or not report.exists():
            abort(404)
        return send_file(report)

    if kind == "chart":
        for path in run["charts"]:
            chart_path = Path(path)
            if chart_path.name == name and chart_path.exists():
                return send_file(chart_path)

    abort(404)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
