"""
routes/auth.py
----------------
Handles: Home, Register, Login, Logout, Forgot Password,
Verify OTP, Reset Password, and Dashboard.

Uses Flask's built-in `session` to remember who is logged in.
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from database import run_query
from services.auth_service import (
    hash_password, verify_password,
    generate_otp, get_otp_expiry, is_otp_valid, send_otp_email
)
from config import Config

auth_bp = Blueprint("auth", __name__)


# ------------------------------------------------------------------
# Helper decorator: protects routes that require the user to be
# logged in. Redirects to the login page otherwise.
# ------------------------------------------------------------------
def login_required(view_function):
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to continue.", "warning")
            return redirect(url_for("auth.login"))
        return view_function(*args, **kwargs)
    return wrapped_view


# ------------------------------------------------------------------
# HOME PAGE
# ------------------------------------------------------------------
@auth_bp.route("/")
def home():
    return render_template("home.html")


# ------------------------------------------------------------------
# REGISTER
# ------------------------------------------------------------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # ---------- Validation ----------
        if not full_name or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("auth.register"))

        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "danger")
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash("Password and Confirm Password do not match.", "danger")
            return redirect(url_for("auth.register"))

        existing_user = run_query(
            "SELECT id FROM users WHERE email = %s", (email,), fetchone=True
        )
        if existing_user:
            flash("This email is already registered. Please login.", "danger")
            return redirect(url_for("auth.register"))

        # ---------- Save user ----------
        hashed = hash_password(password)
        run_query(
            "INSERT INTO users (full_name, email, password) VALUES (%s, %s, %s)",
            (full_name, email, hashed),
            commit=True
        )

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


# ------------------------------------------------------------------
# LOGIN
# ------------------------------------------------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = run_query(
            "SELECT * FROM users WHERE email = %s", (email,), fetchone=True
        )

        if not user or not verify_password(password, user["password"]):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.login"))

        # Save minimal info in the session
        session["user_id"] = user["id"]
        session["full_name"] = user["full_name"]

        flash(f"Welcome back, {user['full_name']}!", "success")
        return redirect(url_for("auth.dashboard"))

    return render_template("login.html")


# ------------------------------------------------------------------
# LOGOUT
# ------------------------------------------------------------------
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.home"))


# ------------------------------------------------------------------
# FORGOT PASSWORD -> generates an OTP and emails it to whichever
# email address the user types into the form (dynamic, per user)
# ------------------------------------------------------------------
@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        # This is the email the CURRENT user typed into the form.
        # It changes every time — it is NOT the sender email in config.py.
        email = request.form.get("email", "").strip().lower()

        user = run_query(
            "SELECT id FROM users WHERE email = %s", (email,), fetchone=True
        )
        if not user:
            flash("No account found with that email.", "danger")
            return redirect(url_for("auth.forgot_password"))

        otp = generate_otp()
        expiry = get_otp_expiry(Config.OTP_EXPIRY_MINUTES)

        run_query(
            "UPDATE users SET otp = %s, otp_expiry = %s WHERE email = %s",
            (otp, expiry, email),
            commit=True
        )

        # Send the OTP to THIS user's email address (the one they typed above).
        email_sent = send_otp_email(email, otp)

        session["reset_email"] = email

        if email_sent:
            flash(f"An OTP has been sent to {email}. Please check your inbox (and spam folder).", "success")
        else:
            # Email failed (e.g. bad SMTP credentials in config.py) -
            # fall back to letting the developer see it in the console
            # so testing isn't blocked.
            flash("Could not send email right now. Check the server console for your OTP, or verify your email settings.", "warning")

        return redirect(url_for("auth.verify_otp"))

    return render_template("forgot_password.html")


# ------------------------------------------------------------------
# VERIFY OTP
# ------------------------------------------------------------------
@auth_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    email = session.get("reset_email")
    if not email:
        flash("Please start the forgot password process again.", "warning")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        entered_otp = request.form.get("otp", "").strip()

        user = run_query(
            "SELECT otp, otp_expiry FROM users WHERE email = %s",
            (email,), fetchone=True
        )

        if not user or not is_otp_valid(user["otp"], entered_otp, user["otp_expiry"]):
            flash("Invalid or expired OTP. Please try again.", "danger")
            return redirect(url_for("auth.verify_otp"))

        session["otp_verified"] = True
        flash("OTP verified. Please set a new password.", "success")
        return redirect(url_for("auth.reset_password"))

    return render_template("verify_otp.html")


# ------------------------------------------------------------------
# RESET PASSWORD
# ------------------------------------------------------------------
@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    email = session.get("reset_email")
    if not email or not session.get("otp_verified"):
        flash("Please verify your OTP first.", "warning")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        new_password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if len(new_password) < 8:
            flash("Password must be at least 8 characters long.", "danger")
            return redirect(url_for("auth.reset_password"))

        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.reset_password"))

        hashed = hash_password(new_password)
        run_query(
            "UPDATE users SET password = %s, otp = NULL, otp_expiry = NULL WHERE email = %s",
            (hashed, email),
            commit=True
        )

        # Clean up session
        session.pop("reset_email", None)
        session.pop("otp_verified", None)

        flash("Password reset successful. Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html")


# ------------------------------------------------------------------
# DASHBOARD
# ------------------------------------------------------------------
@auth_bp.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]

    portfolio = run_query(
        "SELECT status, portfolio_url FROM portfolio WHERE user_id = %s ORDER BY id DESC LIMIT 1",
        (user_id,), fetchone=True
    )
    latest_ats = run_query(
        "SELECT score FROM ats_score WHERE user_id = %s ORDER BY id DESC LIMIT 1",
        (user_id,), fetchone=True
    )

    return render_template(
        "dashboard.html",
        full_name=session.get("full_name"),
        portfolio=portfolio,
        latest_ats=latest_ats
    )