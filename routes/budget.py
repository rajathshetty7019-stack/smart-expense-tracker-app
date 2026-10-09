from datetime import date
from decimal import Decimal

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    url_for
)
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import DecimalField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

from extensions import db
from models import Budget, Transaction


budget_bp = Blueprint(
    "budget",
    __name__,
    url_prefix="/budget"
)


class BudgetForm(FlaskForm):
    """Form for creating or updating a monthly budget."""

    amount = DecimalField(
        "Monthly Budget",
        validators=[
            DataRequired(),
            NumberRange(
                min=0.01,
                message="Budget must be greater than 0."
            )
        ],
        places=2
    )

    month = IntegerField(
        "Month",
        validators=[
            DataRequired(),
            NumberRange(
                min=1,
                max=12,
                message="Month must be between 1 and 12."
            )
        ]
    )

    year = IntegerField(
        "Year",
        validators=[
            DataRequired(),
            NumberRange(
                min=2020,
                max=2100,
                message="Enter a valid year."
            )
        ]
    )

    submit = SubmitField("Save Budget")


@budget_bp.route("/", methods=["GET", "POST"])
@login_required
def budget():
    """Create or update a monthly budget."""

    today = date.today()

    form = BudgetForm()

    # Use current month/year as defaults
    if not form.is_submitted():
        form.month.data = today.month
        form.year.data = today.year

    if form.validate_on_submit():

        month = form.month.data
        year = form.year.data

        existing_budget = Budget.query.filter_by(
            user_id=current_user.id,
            month=month,
            year=year
        ).first()

        if existing_budget:

            existing_budget.amount = form.amount.data

            message = "Budget updated successfully."

        else:

            new_budget = Budget(
                user_id=current_user.id,
                month=month,
                year=year,
                amount=form.amount.data
            )

            db.session.add(new_budget)

            message = "Budget created successfully."

        db.session.commit()

        flash(
            message,
            "success"
        )

        return redirect(
            url_for("budget.budget")
        )

    # Current month's budget
    current_budget = Budget.query.filter_by(
        user_id=current_user.id,
        month=today.month,
        year=today.year
    ).first()

    # Current month's expenses
    current_expenses = db.session.query(
        db.func.coalesce(
            db.func.sum(Transaction.amount),
            0
        )
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "Expense",
        db.extract("month", Transaction.date) == today.month,
        db.extract("year", Transaction.date) == today.year
    ).scalar()

    current_expenses = Decimal(
        str(current_expenses or 0)
    )

    budget_amount = Decimal("0.00")

    if current_budget:
        budget_amount = Decimal(
            str(current_budget.amount)
        )

    remaining = budget_amount - current_expenses

    percentage = Decimal("0.00")

    if budget_amount > 0:
        percentage = (
            current_expenses / budget_amount
        ) * Decimal("100")

        if percentage > 100:
            percentage = Decimal("100")

    return render_template(
        "budget.html",
        form=form,
        current_budget=current_budget,
        budget_amount=budget_amount,
        current_expenses=current_expenses,
        remaining=remaining,
        percentage=percentage,
        current_month=today.month,
        current_year=today.year
    )