# ATS Analyzer

A Flask web app that scores a resume the way an Applicant Tracking System
(ATS) would, with or without a job description, and gives clear, visual
feedback on what to fix.

## Features
- Upload resume as **PDF or DOCX**
- Job description is **optional** — if you skip it, the app scores your
  resume against common skills for the role's detected domain
  (software engineering, data science, marketing, HR, finance, etc.)
- Overall score out of 100, plus a category breakdown (keyword match,
  formatting, experience quality, spelling & grammar)
- Donut, bar, and pie charts for a quick visual read
- Missing keyword suggestions
- Basic spelling-mistake detection
- Scan history dashboard with a score trend line

## Project structure
```
ats_analyzer/
├── app.py            # Flask routes
├── ats.py            # Scoring engine
├── parser.py         # PDF/DOCX text extraction + domain detection
├── report.py         # Chart data + report persistence
├── database.py        # SQLite scan history
├── config.py          # App configuration
├── utils.py            # Helpers: spelling, skill bank, contact extraction
├── requirements.txt
├── uploads/            # Uploaded resumes (created automatically)
├── reports/            # Saved JSON reports (created automatically)
├── database/            # SQLite file (created automatically)
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── result.html
│   └── dashboard.html
└── static/
    ├── style.css
    ├── script.js
    └── images/
```

## Setup

1. Create a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the app:
   ```
   python app.py
   ```

4. Open `http://127.0.0.1:5000` in your browser.

## Notes
- Spelling detection uses `pyspellchecker` with a whitelist of common
  tech/business terms so things like "Python" or "SEO" aren't flagged.
- Keyword matching uses TF-IDF + cosine similarity when a job description
  is supplied, and a curated skill bank per domain when it isn't.
- Reports are stored both in SQLite (for the dashboard) and as JSON
  snapshots in `reports/`.

## Ideas for extending this
- Add user accounts so history is per-user instead of global
- Support `.txt`/`.rtf` uploads
- Swap the skill bank for a live O*NET / LinkedIn skills API
- Add a "before vs after" diff view when re-scanning an edited resume
