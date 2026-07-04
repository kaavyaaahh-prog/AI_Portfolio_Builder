"""
routes/resume.py
------------------
Handles resume upload (PDF only, max 5MB), text extraction,
and kicks off AI portfolio generation.
"""

import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app

from database import run_query
from routes.auth import login_required
from services.pdf_parser import extract_text_from_pdf
from config import Config

resume_bp = Blueprint("resume", __name__)


def _allowed_file(filename: str) -> bool:
    """Check the uploaded file has a .pdf extension."""
    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@resume_bp.route("/upload-resume", methods=["GET", "POST"])
@login_required
def upload_resume():
    if request.method == "POST":
        user_id = session["user_id"]

        if "resume_file" not in request.files:
            flash("No file selected.", "danger")
            return redirect(url_for("resume.upload_resume"))

        file = request.files["resume_file"]

        if file.filename == "":
            flash("No file selected.", "danger")
            return redirect(url_for("resume.upload_resume"))

        if not _allowed_file(file.filename):
            flash("Only PDF files are allowed.", "danger")
            return redirect(url_for("resume.upload_resume"))

        # ---------- Save file to uploads/resumes/ ----------
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        safe_filename = f"user_{user_id}_{file.filename}"
        save_path = os.path.join(Config.UPLOAD_FOLDER, safe_filename)
        file.save(save_path)

        # ---------- Extract text with PyMuPDF ----------
        resume_text = extract_text_from_pdf(save_path)

        if not resume_text:
            flash("Could not read text from this PDF. Please try another file.", "danger")
            return redirect(url_for("resume.upload_resume"))

        # ---------- Save to MySQL ----------
        run_query(
            "INSERT INTO resume (user_id, resume_file, resume_text) VALUES (%s, %s, %s)",
            (user_id, safe_filename, resume_text),
            commit=True
        )

        flash("Resume uploaded successfully! Generating your portfolio...", "success")
        return redirect(url_for("portfolio.generate_portfolio"))

    return render_template("upload_resume.html")
