"""
app.py
-------
Main entry point for the AI Portfolio Builder Flask application.
Run this file to start the development server:

    python app.py

Then open: http://localhost:5000
"""

import os
from flask import Flask

from config import Config
from routes.auth import auth_bp
from routes.resume import resume_bp
from routes.portfolio import portfolio_bp
from routes.ats import ats_bp
from routes.internship import internship_bp

# ------------------------------------------------------------------
# The HTML templates live in ../frontend and static files (css/js/images)
# also live in ../frontend, so we point Flask at that folder directly.
# ------------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATE_DIR = os.path.join(BASE_DIR, "frontend")
STATIC_DIR = os.path.join(BASE_DIR, "frontend")

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR,
    static_url_path="/static"
)
app.config.from_object(Config)

# Make sure the resume upload folder exists
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# ------------------------------------------------------------------
# Register all blueprints (route modules)
# ------------------------------------------------------------------
app.register_blueprint(auth_bp)
app.register_blueprint(resume_bp)
app.register_blueprint(portfolio_bp)
app.register_blueprint(ats_bp)
app.register_blueprint(internship_bp)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
