"""
config.py
----------
All application configuration values live here.
Beginners: change these values to match your own computer setup.
"""

import os

# Base directory of the whole project (one level above /backend)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Config:
    # ---------------- Flask ----------------
    SECRET_KEY = "change-this-secret-key-in-production"

    # ---------------- MySQL ----------------
    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "your_mysql_password"   # <-- change this
    MYSQL_DATABASE = "ai_portfolio_builder"

    # ---------------- File Upload ----------------
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "resumes")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024      # 5 MB max upload size
    ALLOWED_EXTENSIONS = {"pdf"}

    # ---------------- Ollama AI ----------------
    OLLAMA_URL = "http://localhost:11434/api/generate"
    OLLAMA_MODEL = "llama3.1"

    # ---------------- OTP ----------------
    OTP_EXPIRY_MINUTES = 5

    # ---------------- Internship Finder (Adzuna Jobs API) ----------------
    # This powers Module: "Upload Resume -> Internship Recommendations".
    # Adzuna has a FREE tier that returns REAL, currently-live job/internship
    # listings (not fake/sample data). To activate real listings:
    #   1. Go to https://developer.adzuna.com/ and click "Register".
    #   2. Create a free account -> you'll get an "Application ID" and
    #      "Application Key" instantly on your dashboard.
    #   3. Paste them below.
    # Until you add real keys, the page will still work and will show
    # rule-based recommended roles from the resume, but the live
    # "Current Openings" list will show a setup notice instead of results.
    ADZUNA_APP_ID = "e09f6fcf"     # <-- change this
    ADZUNA_APP_KEY = "9c2dabd0b098f83b6dd76200ced9f451"   # <-- change this
    ADZUNA_COUNTRY = "in"                    # "in"=India, "gb"=UK, "us"=USA, etc.
    ADZUNA_DEFAULT_LOCATION = "Coimbatore"   # used if the resume has no location
    ADZUNA_RESULTS_PER_PAGE = 20

    # ---------------- Email (SMTP) ----------------
    # Used to actually send the OTP to the user's email during
    # the Forgot Password flow.
    #
    # For Gmail:
    #   1. Turn on 2-Step Verification on your Google account.
    #   2. Go to Google Account -> Security -> App Passwords.
    #   3. Generate a 16-character App Password for "Mail".
    #   4. Put your Gmail address in MAIL_USERNAME and the
    #      16-character App Password (NOT your normal Gmail
    #      password) in MAIL_PASSWORD below.
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "your_email@gmail.com"        # <-- change this
    MAIL_PASSWORD = "your_16_char_app_password"   # <-- change this
    MAIL_FROM_NAME = "AI Portfolio Builder"

    # If True, OTP is also printed to the console (handy for debugging).
    # Set to False once real email sending is confirmed working.
    MAIL_DEBUG_PRINT_OTP = True