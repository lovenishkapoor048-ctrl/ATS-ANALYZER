"""
report.py
Turns a raw analysis dict (from ats.ATSAnalyzer) into chart-ready JSON
for the frontend, and optionally persists a copy to disk as a record.
"""

import json
import os
from datetime import datetime

from config import Config


def build_chart_data(analysis: dict) -> dict:
    score = analysis["overall_score"]
    categories = analysis["category_scores"]

    return {
        "score_donut": {
            "labels": ["Score", "Remaining"],
            "data": [score, max(0, 100 - score)],
        },
        "category_bar": {
            "labels": list(categories.keys()),
            "data": list(categories.values()),
        },
        "keyword_pie": {
            "labels": ["Matched Keywords", "Missing Keywords"],
            "data": [
                len(analysis["matched_keywords"]),
                len(analysis["missing_keywords"]),
            ],
        },
    }


def save_report(analysis: dict, original_filename: str) -> str:
    """Save the analysis as a timestamped JSON file. Returns the file path."""
    os.makedirs(Config.REPORTS_FOLDER, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_name = os.path.splitext(original_filename)[0][:40]
    out_path = os.path.join(Config.REPORTS_FOLDER, f"{timestamp}_{safe_name}.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2)

    return out_path
