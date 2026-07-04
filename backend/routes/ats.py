"""
routes/ats.py
---------------
Handles the ATS (Applicant Tracking System) resume score feature.
Reuses the most recently uploaded resume's extracted text.
"""

import json
from flask import Blueprint, render_template, redirect, url_for, session, flash

from database import run_query
from routes.auth import login_required
from services.ollama_service import generate_ats_score

ats_bp = Blueprint("ats", __name__)


@ats_bp.route("/ats-score")
@login_required
def ats_score():
    user_id = session["user_id"]

    latest_resume = run_query(
        "SELECT resume_text FROM resume WHERE user_id = %s ORDER BY id DESC LIMIT 1",
        (user_id,), fetchone=True
    )

    if not latest_resume or not latest_resume["resume_text"]:
        flash("Please upload a resume first to get your ATS score.", "warning")
        return redirect(url_for("resume.upload_resume"))

    result = generate_ats_score(latest_resume["resume_text"])

    run_query(
        """INSERT INTO ats_score (user_id, score, strengths, weaknesses, suggestions, keywords)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (
            user_id,
            result.get("overall_score", 0),
            json.dumps(result.get("strengths", [])),
            json.dumps(result.get("weaknesses", [])),
            json.dumps(result.get("suggestions", [])),
            json.dumps(result.get("missing_keywords", [])),
        ),
        commit=True
    )

    return render_template("ats_score.html", result=result)
