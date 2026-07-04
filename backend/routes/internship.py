"""
routes/internship.py
----------------------
MODULE: Internship Recommendations
Reads the student's latest resume/portfolio skills, suggests matching
internship roles, and fetches REAL current internship/job openings
(title, company, location, salary, apply link) for those roles from
the Adzuna Jobs API.
"""

import json
from flask import Blueprint, render_template, request, session, redirect, url_for, flash

from database import run_query
from routes.auth import login_required
from services.internship_service import recommend_roles, search_internships

internship_bp = Blueprint("internship", __name__)


def _json_or_default(value, default):
    if not value:
        return default
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default


@internship_bp.route("/internship-recommendations", methods=["GET"])
@login_required
def internship_recommendations():
    user_id = session["user_id"]

    portfolio = run_query(
        "SELECT skills FROM portfolio WHERE user_id = %s ORDER BY id DESC LIMIT 1",
        (user_id,), fetchone=True
    )

    if not portfolio:
        flash("Please upload your resume first so we can recommend internships for you.", "warning")
        return redirect(url_for("resume.upload_resume"))

    skills = _json_or_default(portfolio["skills"], {"technical_skills": [], "soft_skills": []})
    recommended_roles = recommend_roles(skills)

    # Selected role + location come from the filter form (GET query params),
    # defaulting to the top recommended role.
    selected_role = request.args.get("role", "").strip() or (recommended_roles[0] if recommended_roles else "Internship")
    location = request.args.get("location", "").strip()

    search_result = search_internships(selected_role, location)

    if not search_result.get("configured"):
        flash(
            "Live internship listings need a free Adzuna API key. "
            "Add ADZUNA_APP_ID and ADZUNA_APP_KEY in backend/config.py "
            "(sign up free at https://developer.adzuna.com/) to see real openings.",
            "info"
        )

    return render_template(
        "internship_recommendations.html",
        recommended_roles=recommended_roles,
        selected_role=selected_role,
        location=location,
        listings=search_result.get("results", []),
        configured=search_result.get("configured", False),
        technical_skills=skills.get("technical_skills", []),
    )
