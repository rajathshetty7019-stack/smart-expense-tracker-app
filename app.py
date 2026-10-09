from flask import Flask, render_template, redirect, url_for
import os

from config import Config
from extensions import db, login_manager
from routes.auth import auth_bp
from routes.transactions import transactions_bp
from routes.budget import budget_bp
from routes.reports import reports_bp
from routes.recurring import recurring_bp
from apscheduler.schedulers.background import BackgroundScheduler

def process_all_recurring_transactions(app):
    from models import User
    from routes.recurring import process_due_transactions

    with app.app_context():
        users = User.query.all()

        for user in users:
            process_due_transactions(user.id)

def create_app():
    """Create and configure the Flask application."""

    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)

    # Initialize Flask-Login
    login_manager.init_app(app)

    # Configure login page
    login_manager.login_view = "auth.login"

    # Import models
    from models import User, Transaction, Budget

    from models.recurring_transaction import (
    RecurringTransaction,
    RecurringTransactionOccurrence,
)
    # Load user for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(
            User,
            int(user_id)
        )

    # Register authentication routes
    app.register_blueprint(auth_bp)

    # Register transaction routes
    app.register_blueprint(transactions_bp)

    app.register_blueprint(budget_bp)

    app.register_blueprint(reports_bp)

    app.register_blueprint(recurring_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    scheduler = BackgroundScheduler(daemon=True)

    scheduler.add_job(
        func=lambda: process_all_recurring_transactions(app),
        trigger="interval",
        hours=24,
        id="recurring_transactions",
        replace_existing=True,
    )

    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
         scheduler.start()
         print("Scheduler started:", scheduler.running)
         print("Scheduled jobs:", scheduler.get_jobs())

    # Home page
    @app.route("/")
    def index():
       return redirect(url_for("transactions.dashboard"))
       
    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)