from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from extensions import db
from models import User


auth_bp = Blueprint("auth", __name__)


# ============================================================
# REGISTRATION FORM
# ============================================================

class RegisterForm(FlaskForm):
    """Form used to create a new user account."""

    username = StringField(
        "Username",
        validators=[
            DataRequired(message="Username is required."),
            Length(
                min=3,
                max=80,
                message="Username must be between 3 and 80 characters."
            )
        ]
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Please enter a valid email address."),
            Length(
                max=120,
                message="Email cannot exceed 120 characters."
            )
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required."),
            Length(
                min=6,
                max=128,
                message="Password must be between 6 and 128 characters."
            )
        ]
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(message="Please confirm your password."),
            EqualTo(
                "password",
                message="Passwords must match."
            )
        ]
    )


# ============================================================
# LOGIN FORM
# ============================================================

class LoginForm(FlaskForm):
    """Form used to log an existing user into the application."""

    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email is required.")
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required.")
        ]
    )


# ============================================================
# REGISTER
# ============================================================

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user."""

    form = RegisterForm()

    if form.validate_on_submit():

        username = form.username.data.strip()
        email = form.email.data.strip().lower()

        # Check whether username already exists
        existing_username = User.query.filter_by(
            username=username
        ).first()

        if existing_username:
            flash(
                "Username already exists. Please choose another.",
                "error"
            )

            return render_template(
                "register.html",
                form=form
            )

        # Check whether email already exists
        existing_email = User.query.filter_by(
            email=email
        ).first()

        if existing_email:
            flash(
                "Email is already registered. Please use another email.",
                "error"
            )

            return render_template(
                "register.html",
                form=form
            )

        # Create new user
        user = User(
            username=username,
            email=email
        )

        # Hash and save password
        user.set_password(
            form.password.data
        )

        # Save user to database
        db.session.add(user)
        db.session.commit()

        flash(
            "Registration successful! You can now log in.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "register.html",
        form=form
    )


# ============================================================
# LOGIN
# ============================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Log an existing user into the application."""

    form = LoginForm()

    if form.validate_on_submit():

        # Get email entered by user
        email = form.email.data.strip().lower()

        # Find user by email
        user = User.query.filter_by(
            email=email
        ).first()

        # Check user and password
        if user and user.check_password(
            form.password.data
        ):

            # Log the user in
            login_user(user)

            flash(
                "Login successful!",
                "success"
            )

            return redirect(
                url_for("index")
            )

        # Login failed
        flash(
            "Invalid email or password.",
            "error"
        )

    return render_template(
        "login.html",
        form=form
    )


# ============================================================
# LOGOUT
# ============================================================

@auth_bp.route("/logout")
@login_required
def logout():
    """Log the current user out."""

    logout_user()

    flash(
        "You have been logged out successfully.",
        "success"
    )

    return redirect(
        url_for("auth.login")
    )