"""
routes/portfolio.py
---------------------
Handles: AI portfolio generation, preview, edit, save (draft),
publish, and the public portfolio view page.
"""

import json
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from database import run_query
from routes.auth import login_required
from services.ollama_service import generate_portfolio_from_resume

portfolio_bp = Blueprint("portfolio", __name__)

# ------------------------------------------------------------------
# All selectable portfolio themes (must match frontend/css/themes.css)
# ------------------------------------------------------------------
AVAILABLE_THEMES = [
    "midnight", "sunset", "ocean", "forest", "royal", "rosegold",
    "cyberpunk", "minimal", "corporate", "pastel", "crimson",
    "emerald", "arctic", "coffee", "lavender", "golden", "slate",
]


def _json_or_default(value, default):
    """Safely parse a JSON string pulled from the database."""
    if not value:
        return default
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default


# ------------------------------------------------------------------
# MODULE 4: Generate portfolio content from the latest resume using AI
# ------------------------------------------------------------------
@portfolio_bp.route("/generate-portfolio")
@login_required
def generate_portfolio():
    user_id = session["user_id"]

    latest_resume = run_query(
        "SELECT resume_text FROM resume WHERE user_id = %s ORDER BY id DESC LIMIT 1",
        (user_id,), fetchone=True
    )

    if not latest_resume or not latest_resume["resume_text"]:
        flash("Please upload a resume first.", "warning")
        return redirect(url_for("resume.upload_resume"))

    ai_data = generate_portfolio_from_resume(latest_resume["resume_text"])

    if not ai_data:
        flash("AI could not process your resume. Please try again.", "danger")
        return redirect(url_for("resume.upload_resume"))

    skills = ai_data.get("skills", {})

    run_query(
        """INSERT INTO portfolio
           (user_id, name, title, about, career_objective, education, skills,
            projects, certificates, achievements, github, linkedin, phone, email, status)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'draft')""",
        (
            user_id,
            ai_data.get("full_name", ""),
            ai_data.get("professional_title", ""),
            ai_data.get("about_me", ""),
            ai_data.get("career_objective", ""),
            json.dumps(ai_data.get("education", [])),
            json.dumps(skills),
            json.dumps(ai_data.get("projects", [])),
            json.dumps(ai_data.get("certificates", [])),
            json.dumps(ai_data.get("achievements", [])),
            ai_data.get("github", ""),
            ai_data.get("linkedin", ""),
            ai_data.get("phone", ""),
            ai_data.get("email", ""),
        ),
        commit=True
    )

    flash("Your AI-generated portfolio is ready!", "success")
    return redirect(url_for("portfolio.preview_portfolio"))


def _get_latest_portfolio(user_id):
    return run_query(
        "SELECT * FROM portfolio WHERE user_id = %s ORDER BY id DESC LIMIT 1",
        (user_id,), fetchone=True
    )


# ------------------------------------------------------------------
# MODULE 5: Preview portfolio (private, logged-in view)
# ------------------------------------------------------------------
@portfolio_bp.route("/portfolio-preview")
@login_required
def preview_portfolio():
    user_id = session["user_id"]
    portfolio = _get_latest_portfolio(user_id)

    if not portfolio:
        flash("No portfolio found. Please upload a resume first.", "warning")
        return redirect(url_for("resume.upload_resume"))

    portfolio["education"] = _json_or_default(portfolio["education"], [])
    portfolio["skills"] = _json_or_default(portfolio["skills"], {"technical_skills": [], "soft_skills": []})
    portfolio["projects"] = _json_or_default(portfolio["projects"], [])
    portfolio["certificates"] = _json_or_default(portfolio["certificates"], [])
    portfolio["achievements"] = _json_or_default(portfolio["achievements"], [])
    portfolio["theme"] = portfolio.get("theme") or "midnight"

    return render_template(
        "portfolio_preview.html",
        portfolio=portfolio,
        is_public=False,
        available_themes=AVAILABLE_THEMES
    )


# ------------------------------------------------------------------
# MODULE 5b: Change the portfolio's visual theme (1 of 15+ styles)
# ------------------------------------------------------------------
@portfolio_bp.route("/set-portfolio-theme/<string:theme_name>")
@login_required
def set_portfolio_theme(theme_name):
    user_id = session["user_id"]

    if theme_name not in AVAILABLE_THEMES:
        flash("Unknown theme selected.", "danger")
        return redirect(url_for("portfolio.preview_portfolio"))

    portfolio = _get_latest_portfolio(user_id)
    if not portfolio:
        flash("No portfolio found. Please upload a resume first.", "warning")
        return redirect(url_for("resume.upload_resume"))

    run_query(
        "UPDATE portfolio SET theme = %s WHERE id = %s AND user_id = %s",
        (theme_name, portfolio["id"], user_id),
        commit=True
    )

    flash(f"Theme changed to \"{theme_name.title()}\".", "success")
    return redirect(url_for("portfolio.preview_portfolio"))


# ------------------------------------------------------------------
# MODULE 6: Edit portfolio
# ------------------------------------------------------------------
@portfolio_bp.route("/edit-portfolio", methods=["GET", "POST"])
@login_required
def edit_portfolio():
    user_id = session["user_id"]
    portfolio = _get_latest_portfolio(user_id)

    if not portfolio:
        flash("No portfolio found. Please upload a resume first.", "warning")
        return redirect(url_for("resume.upload_resume"))

    if request.method == "POST":
        about = request.form.get("about", "")
        career_objective = request.form.get("career_objective", "")
        technical_skills = [s.strip() for s in request.form.get("technical_skills", "").split(",") if s.strip()]
        soft_skills = [s.strip() for s in request.form.get("soft_skills", "").split(",") if s.strip()]

        project_titles = request.form.getlist("project_title")
        project_descriptions = request.form.getlist("project_description")
        projects = [
            {"title": t, "description": d}
            for t, d in zip(project_titles, project_descriptions) if t.strip()
        ]

        certificates = [c.strip() for c in request.form.get("certificates", "").split(",") if c.strip()]

        run_query(
            """UPDATE portfolio
               SET about = %s, career_objective = %s, skills = %s,
                   projects = %s, certificates = %s
               WHERE id = %s AND user_id = %s""",
            (
                about,
                career_objective,
                json.dumps({"technical_skills": technical_skills, "soft_skills": soft_skills}),
                json.dumps(projects),
                json.dumps(certificates),
                portfolio["id"],
                user_id
            ),
            commit=True
        )

        flash("Portfolio updated successfully!", "success")
        return redirect(url_for("portfolio.preview_portfolio"))

    portfolio["skills"] = _json_or_default(portfolio["skills"], {"technical_skills": [], "soft_skills": []})
    portfolio["projects"] = _json_or_default(portfolio["projects"], [])
    portfolio["certificates"] = _json_or_default(portfolio["certificates"], [])

    return render_template("edit_portfolio.html", portfolio=portfolio)


# ------------------------------------------------------------------
# MODULE 7: Save portfolio as draft (explicit "Save" button)
# ------------------------------------------------------------------
@portfolio_bp.route("/save-portfolio")
@login_required
def save_portfolio():
    user_id = session["user_id"]
    portfolio = _get_latest_portfolio(user_id)

    if portfolio and portfolio["status"] != "published":
        run_query(
            "UPDATE portfolio SET status = 'draft' WHERE id = %s AND user_id = %s",
            (portfolio["id"], user_id),
            commit=True
        )

    flash("Portfolio saved as draft.", "success")
    return redirect(url_for("portfolio.preview_portfolio"))


# ------------------------------------------------------------------
# MODULE 8: Publish portfolio -> makes it public
# ------------------------------------------------------------------
@portfolio_bp.route("/publish-portfolio")
@login_required
def publish_portfolio():
    user_id = session["user_id"]
    portfolio = _get_latest_portfolio(user_id)

    if not portfolio:
        flash("No portfolio found.", "warning")
        return redirect(url_for("resume.upload_resume"))

    public_url = url_for("portfolio.public_portfolio", portfolio_id=portfolio["id"], _external=True)

    run_query(
        "UPDATE portfolio SET status = 'published', portfolio_url = %s WHERE id = %s AND user_id = %s",
        (public_url, portfolio["id"], user_id),
        commit=True
    )

    flash("Portfolio Published Successfully!", "success")
    return redirect(url_for("portfolio.preview_portfolio"))


# ------------------------------------------------------------------
# Public portfolio view -> http://localhost:5000/portfolio/<id>
# ------------------------------------------------------------------
@portfolio_bp.route("/portfolio/<int:portfolio_id>")
def public_portfolio(portfolio_id):
    portfolio = run_query(
        "SELECT * FROM portfolio WHERE id = %s AND status = 'published'",
        (portfolio_id,), fetchone=True
    )

    if not portfolio:
        flash("This portfolio is not published or does not exist.", "warning")
        return redirect(url_for("auth.home"))

    portfolio["education"] = _json_or_default(portfolio["education"], [])
    portfolio["skills"] = _json_or_default(portfolio["skills"], {"technical_skills": [], "soft_skills": []})
    portfolio["projects"] = _json_or_default(portfolio["projects"], [])
    portfolio["certificates"] = _json_or_default(portfolio["certificates"], [])
    portfolio["achievements"] = _json_or_default(portfolio["achievements"], [])
    portfolio["theme"] = portfolio.get("theme") or "midnight"

    return render_template("portfolio_preview.html", portfolio=portfolio, is_public=True, available_themes=AVAILABLE_THEMES)
