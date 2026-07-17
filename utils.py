"""
utils.py
Small reusable helpers: file validation, text cleaning, contact-info
extraction, spelling checks, and the built-in skill bank used when a
candidate has no job description to compare against.
"""

import re
from config import Config

try:
    from spellchecker import SpellChecker
    _spell = SpellChecker(distance=1)
except Exception:  # pragma: no cover - library optional at import time
    _spell = None


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

def allowed_file(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    )


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d{1,3}[\s\-]?)?(\(?\d{2,4}\)?[\s\-]?)?\d{3,4}[\s\-]?\d{3,4}")
LINKEDIN_RE = re.compile(r"linkedin\.com/[a-zA-Z0-9\-_/]+", re.IGNORECASE)


def extract_contact_info(text: str) -> dict:
    email_match = EMAIL_RE.search(text)
    phone_match = PHONE_RE.search(text)
    linkedin_match = LINKEDIN_RE.search(text)
    return {
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
        "linkedin": linkedin_match.group(0) if linkedin_match else None,
    }


SECTION_HEADERS = {
    "experience": ["experience", "work history", "employment history", "professional experience"],
    "education": ["education", "academic background", "qualifications"],
    "skills": ["skills", "technical skills", "core competencies", "key skills"],
    "projects": ["projects", "personal projects", "academic projects"],
    "certifications": ["certifications", "certificates", "licenses"],
    "summary": ["summary", "objective", "profile", "about me"],
}


def find_present_sections(text: str) -> dict:
    lower = text.lower()
    found = {}
    for section, aliases in SECTION_HEADERS.items():
        found[section] = any(alias in lower for alias in aliases)
    return found


# ---------------------------------------------------------------------------
# Spelling
# ---------------------------------------------------------------------------

# Common technical / business terms that a normal English dictionary would
# incorrectly flag as misspelled. Extend this list as needed.
TECH_WHITELIST = {
    "javascript", "typescript", "python", "django", "flask", "nodejs", "node",
    "react", "reactjs", "vuejs", "angular", "nextjs", "graphql", "mysql",
    "postgresql", "mongodb", "sqlite", "redis", "kubernetes", "docker",
    "devops", "aws", "azure", "gcp", "html", "css", "sass", "api", "apis",
    "rest", "restful", "json", "xml", "linux", "unix", "github", "gitlab",
    "bitbucket", "jira", "figma", "photoshop", "excel", "powerpoint",
    "tensorflow", "pytorch", "keras", "sklearn", "pandas", "numpy",
    "tableau", "powerbi", "seo", "sem", "crm", "erp", "saas", "b2b", "b2c",
    "kpi", "kpis", "roi", "ux", "ui", "cicd", "ci", "cd", "agile", "scrum",
    "kanban", "oop", "sdlc", "qa", "etl", "nosql", "npm", "yarn", "webpack",
    "linkedin", "resume", "curriculum", "vitae",
}


def check_spelling(text: str) -> list:
    """Return a list of likely-misspelled words (word-level, best effort)."""
    if _spell is None:
        return []

    words = re.findall(r"[A-Za-z]+", text)
    candidates = []
    seen = set()
    for w in words:
        lw = w.lower()
        if len(lw) < 4 or lw in seen or lw in TECH_WHITELIST:
            continue
        seen.add(lw)
        candidates.append(lw)

    misspelled = _spell.unknown(candidates)
    # Keep original order of first appearance, cap the list for readability
    ordered = [w for w in candidates if w in misspelled]
    return ordered[:40]


# ---------------------------------------------------------------------------
# Action verbs (used to judge "experience quality")
# ---------------------------------------------------------------------------

ACTION_VERBS = {
    "achieved", "administered", "analyzed", "automated", "built", "collaborated",
    "conducted", "created", "delivered", "designed", "developed", "directed",
    "drove", "engineered", "established", "executed", "generated", "implemented",
    "improved", "increased", "initiated", "launched", "led", "managed",
    "mentored", "negotiated", "optimized", "organized", "planned", "produced",
    "reduced", "resolved", "spearheaded", "streamlined", "supervised",
    "transformed", "coordinated", "budgeted",
}


# ---------------------------------------------------------------------------
# Skill bank: used when the candidate has no job description.
# ---------------------------------------------------------------------------

SKILL_BANK = {
    "software_engineering": [
        "python", "java", "c++", "javascript", "typescript", "git", "docker",
        "kubernetes", "aws", "microservices", "rest api", "sql", "algorithms",
        "data structures", "system design", "unit testing", "ci/cd", "agile",
        "linux", "object oriented programming", "debugging", "cloud",
    ],
    "web_development": [
        "html", "css", "javascript", "react", "vue", "angular", "node.js",
        "express", "next.js", "responsive design", "rest api", "webpack",
        "typescript", "bootstrap", "tailwind", "graphql", "sql", "mongodb",
        "git", "seo",
    ],
    "data_science": [
        "python", "r", "sql", "machine learning", "deep learning", "pandas",
        "numpy", "scikit-learn", "tensorflow", "pytorch", "data visualization",
        "statistics", "tableau", "power bi", "nlp", "data cleaning", "etl",
        "big data", "a/b testing", "regression",
    ],
    "digital_marketing": [
        "seo", "sem", "google analytics", "content marketing", "social media",
        "email marketing", "ppc", "brand strategy", "campaign management",
        "google ads", "facebook ads", "copywriting", "market research",
        "conversion rate optimization", "hubspot", "crm",
    ],
    "human_resources": [
        "recruitment", "onboarding", "employee relations", "performance management",
        "payroll", "hris", "talent acquisition", "training and development",
        "compensation and benefits", "labor law", "conflict resolution",
        "workforce planning",
    ],
    "finance": [
        "financial modeling", "forecasting", "budgeting", "excel", "accounting",
        "financial analysis", "risk management", "audit", "gaap", "variance analysis",
        "reconciliation", "sap", "quickbooks", "valuation", "investment analysis",
    ],
    "mechanical_engineering": [
        "autocad", "solidworks", "cad", "product design", "manufacturing",
        "gd&t", "thermodynamics", "finite element analysis", "prototyping",
        "quality control", "lean manufacturing", "six sigma", "matlab",
    ],
    "sales": [
        "lead generation", "crm", "negotiation", "account management",
        "cold calling", "pipeline management", "salesforce", "b2b sales",
        "client relationship management", "closing", "quota attainment",
        "upselling",
    ],
    "graphic_design": [
        "photoshop", "illustrator", "figma", "indesign", "typography",
        "branding", "ui design", "adobe creative suite", "wireframing",
        "prototyping", "color theory", "layout design",
    ],
    "general": [
        "communication", "leadership", "teamwork", "problem solving",
        "project management", "time management", "microsoft office",
        "critical thinking", "adaptability", "presentation skills",
    ],
}
