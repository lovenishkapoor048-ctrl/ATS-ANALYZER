"""
app.py
Main Flask application. Handles resume upload, runs the ATS analysis,
stores results, and renders the UI pages.
"""

import json
import os

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from werkzeug.utils import secure_filename

from config import Config
from utils import allowed_file
from parser import extract_text
from ats import ATSAnalyzer
from report import build_chart_data, save_report
import database

app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.REPORTS_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)

database.init_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    resume_file = request.files.get("resume")
    job_title = request.form.get("job_title", "").strip()
    job_description = request.form.get("job_description", "").strip()

    if not resume_file or resume_file.filename == "":
        flash("Please choose a resume file (PDF or DOCX).", "error")
        return redirect(url_for("index"))

    if not allowed_file(resume_file.filename):
        flash("Only PDF and DOCX files are supported.", "error")
        return redirect(url_for("index"))

    filename = secure_filename(resume_file.filename)
    saved_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    resume_file.save(saved_path)

    try:
        resume_text = extract_text(saved_path)
    except Exception as exc:
        flash(f"Could not read the resume file: {exc}", "error")
        return redirect(url_for("index"))

    if not resume_text.strip():
        flash("We couldn't extract any text from that file. Try a different file.", "error")
        return redirect(url_for("index"))

    analyzer = ATSAnalyzer(resume_text, job_description or None)
    analysis = analyzer.analyze()
    analysis["job_title"] = job_title or "General Application"

    chart_data = build_chart_data(analysis)
    save_report(analysis, filename)
    scan_id = database.save_scan(filename, job_title, analysis)

    return render_template(
        "result.html",
        analysis=analysis,
        chart_data=json.dumps(chart_data),
        scan_id=scan_id,
    )


@app.route("/history/<int:scan_id>")
def view_history_scan(scan_id):
    scan = database.get_scan_by_id(scan_id)
    if not scan:
        abort(404)

    analysis = scan["details"]
    chart_data = build_chart_data(analysis)

    return render_template(
        "result.html",
        analysis=analysis,
        chart_data=json.dumps(chart_data),
        scan_id=scan_id,
    )


@app.route("/dashboard")
def dashboard():
    history = database.get_history(limit=25)
    trend = {
        "labels": [h["created_at"][:10] for h in reversed(history)],
        "data": [h["overall_score"] for h in reversed(history)],
    }
    return render_template("dashboard.html", history=history, trend=json.dumps(trend))


@app.errorhandler(413)
def file_too_large(_e):
    flash("File is too large. Please upload a resume under 8 MB.", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
