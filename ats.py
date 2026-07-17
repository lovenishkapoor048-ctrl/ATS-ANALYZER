"""
ats.py
The core scoring engine. Given resume text (and optionally a job
description), produces an overall ATS score out of 100, a breakdown by
category, matched/missing keywords, spelling issues, and suggestions.
"""

import re
from collections import Counter

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import Config
from utils import (
    ACTION_VERBS,
    SKILL_BANK,
    check_spelling,
    find_present_sections,
    extract_contact_info,
)
from parser import detect_domain

STOPWORDS = set("""
a about above after again against all am an and any are aren't as at be
because been before being below between both but by can't cannot could
couldn't did didn't do does doesn't doing don't down during each few for
from further had hadn't has hasn't have haven't having he he'd he'll he's
her here here's hers herself him himself his how how's i i'd i'll i'm i've
if in into is isn't it it's its itself let's me more most mustn't my
myself no nor not of off on once only or other ought our ours ourselves
out over own same shan't she she'd she'll she's should shouldn't so some
such than that that's the their theirs them themselves then there there's
these they they'd they'll they're they've this those through to too
under until up very was wasn't we we'd we'll we're we've were weren't
what what's when when's where where's which while who who's whom why
why's with won't would wouldn't you you'd you'll you're you've your
yours yourself yourselves
""".split())


def _extract_keywords(text: str, top_n: int = 30):
    """Pull the most frequent meaningful words/phrases out of a text block."""
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.\-]{1,}", text.lower())
    words = [w.strip(".-") for w in words if w not in STOPWORDS and len(w) > 2]
    freq = Counter(words)
    return [w for w, _ in freq.most_common(top_n)]


class ATSAnalyzer:
    def __init__(self, resume_text: str, job_description: str = None):
        self.resume_text = resume_text or ""
        self.job_description = (job_description or "").strip()
        self.resume_lower = self.resume_text.lower()

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def analyze(self) -> dict:
        domain = detect_domain(self.resume_text)

        if self.job_description:
            keyword_score, matched, missing = self._keyword_match_with_jd()
        else:
            keyword_score, matched, missing = self._keyword_match_with_bank(domain)

        formatting_score, formatting_notes = self._formatting_score()
        experience_score, experience_notes = self._experience_score()

        spelling_errors = check_spelling(self.resume_text)
        spelling_score = max(0, 100 - len(spelling_errors) * 4)

        category_scores = {
            "Keyword Match": round(keyword_score),
            "Formatting": round(formatting_score),
            "Experience Quality": round(experience_score),
            "Spelling & Grammar": round(spelling_score),
        }

        weights = Config.SCORE_WEIGHTS
        overall_score = round(sum(category_scores[k] * weights[k] for k in weights))
        overall_score = max(0, min(100, overall_score))

        suggestions = self._build_suggestions(
            category_scores, missing, formatting_notes, experience_notes, spelling_errors
        )

        return {
            "overall_score": overall_score,
            "category_scores": category_scores,
            "matched_keywords": matched[:20],
            "missing_keywords": missing[:20],
            "domain": domain.replace("_", " ").title(),
            "spelling_errors": spelling_errors[:15],
            "suggestions": suggestions,
            "word_count": len(self.resume_text.split()),
            "used_job_description": bool(self.job_description),
        }

    # ------------------------------------------------------------------
    # Keyword matching
    # ------------------------------------------------------------------
    def _keyword_match_with_jd(self):
        try:
            vectorizer = TfidfVectorizer(stop_words="english")
            matrix = vectorizer.fit_transform([self.resume_text, self.job_description])
            similarity = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        except ValueError:
            similarity = 0.0

        score = round(similarity * 100, 2)

        jd_keywords = _extract_keywords(self.job_description, top_n=25)
        matched = [kw for kw in jd_keywords if kw in self.resume_lower]
        missing = [kw for kw in jd_keywords if kw not in self.resume_lower]

        return score, matched, missing

    def _keyword_match_with_bank(self, domain: str):
        skills = SKILL_BANK.get(domain, SKILL_BANK["general"])
        matched = [s for s in skills if s in self.resume_lower]
        missing = [s for s in skills if s not in self.resume_lower]

        score = (len(matched) / len(skills)) * 100 if skills else 0
        return score, matched, missing

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------
    def _formatting_score(self):
        notes = []
        score = 100.0

        contact = extract_contact_info(self.resume_text)
        if not contact["email"]:
            score -= 15
            notes.append("No email address detected — add one so recruiters can reach you.")
        if not contact["phone"]:
            score -= 10
            notes.append("No phone number detected.")

        sections = find_present_sections(self.resume_text)
        for section in ("experience", "education", "skills"):
            if not sections.get(section):
                score -= 12
                notes.append(f"Missing a clear '{section.title()}' section.")

        word_count = len(self.resume_text.split())
        if word_count < Config.IDEAL_WORD_COUNT_MIN:
            score -= 10
            notes.append("Resume looks too short — add more detail on your experience.")
        elif word_count > Config.IDEAL_WORD_COUNT_MAX:
            score -= 10
            notes.append("Resume looks long — trim it to keep it focused and scannable.")

        bullet_count = self.resume_text.count("•") + len(re.findall(r"^\s*[-*]\s", self.resume_text, re.MULTILINE))
        if bullet_count < 3:
            score -= 8
            notes.append("Use more bullet points to make achievements easy to scan.")

        return max(0, score), notes

    # ------------------------------------------------------------------
    # Experience quality
    # ------------------------------------------------------------------
    def _experience_score(self):
        notes = []
        words = re.findall(r"[a-zA-Z']+", self.resume_lower)
        action_verb_hits = sum(1 for w in words if w in ACTION_VERBS)

        quantified_hits = len(re.findall(r"\d+(\.\d+)?\s*(%|percent|\$|k\b|million|hours|days|users|clients)", self.resume_lower))

        score = 40.0
        score += min(action_verb_hits * 4, 35)
        score += min(quantified_hits * 8, 25)

        if action_verb_hits < 4:
            notes.append("Use more strong action verbs (e.g. 'led', 'built', 'optimized') to start bullet points.")
        if quantified_hits < 2:
            notes.append("Add quantifiable results (e.g. 'increased revenue by 20%', 'managed a team of 5').")

        return min(100, score), notes

    # ------------------------------------------------------------------
    # Suggestions
    # ------------------------------------------------------------------
    def _build_suggestions(self, category_scores, missing_keywords, formatting_notes, experience_notes, spelling_errors):
        suggestions = []

        if missing_keywords:
            top_missing = ", ".join(missing_keywords[:8])
            suggestions.append(f"Add these missing keywords/skills if relevant: {top_missing}.")

        suggestions.extend(formatting_notes)
        suggestions.extend(experience_notes)

        if spelling_errors:
            preview = ", ".join(spelling_errors[:6])
            suggestions.append(f"Fix possible spelling issues: {preview}.")

        if category_scores["Keyword Match"] < 50:
            suggestions.append("Your resume's keyword overlap is low — tailor it more closely to the role you're targeting.")

        if not suggestions:
            suggestions.append("Great work — your resume covers the essentials well. Keep tailoring it per job description.")

        return suggestions[:12]
