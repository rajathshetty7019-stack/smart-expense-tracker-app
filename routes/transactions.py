import csv
from datetime import date
from io import StringIO

from flask import (
    Blueprint,
    Response,
    flash,
    redirect,
    render_template,
    url_for,
)
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    DecimalField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, NumberRange, Optional

from extensions import db
from models.transaction import Transaction
from models.budget import Budget


transactions_bp = Blueprint(
    "transactions",
    __name__,
    url_prefix="/transactions",
)


class TransactionForm(FlaskForm):
    amount = DecimalField(
        "Amount",
        validators=[
            DataRequired(),
            NumberRange(min=0.01),
        ],
    )

    type = SelectField(
        "Type",
        choices=[
            ("income", "Income"),
            ("expense", "Expense"),
        ],
        validators=[DataRequired()],
    )

    category = StringField(
        "Category",
        validators=[DataRequired()],
    )

    description = StringField(
        "Description",
        validators=[Optional()],
    )

    date = DateField(
        "Date",
        default=date.today,
        validators=[DataRequired()],
    )

    submit = SubmitField("Save Transaction")


class DeleteForm(FlaskForm):
    """CSRF-protected form for transaction deletion."""
    pass


@transactions_bp.route("/dashboard")
@login_required
def dashboard():
    transactions = (
        Transaction.query
        .filter_by(user_id=current_user.id)
        .order_by(Transaction.date.desc(), Transaction.id.desc())
        .all()
    )

    total_income = sum(
        float(t.amount)
        for t in transactions
        if t.type == "income"
    )

    total_expenses = sum(
        float(t.amount)
        for t in transactions
        if t.type == "expense"
    )

    balance = total_income - total_expenses

    today = date.today()

    monthly_transactions = [
        t for t in transactions
        if t.date.year == today.year
        and t.date.month == today.month
    ]

    monthly_income = sum(
        float(t.amount)
        for t in monthly_transactions
        if t.type == "income"
    )

    monthly_expenses = sum(
        float(t.amount)
        for t in monthly_transactions
        if t.type == "expense"
    )

    monthly_savings = monthly_income - monthly_expenses

    current_budget = (
        Budget.query
        .filter_by(
            user_id=current_user.id,
            month=today.month,
            year=today.year,
        )
        .first()
    )

    budget_amount = (
        float(current_budget.amount)
        if current_budget
        else 0.0
    )

    if budget_amount > 0:
        budget_used_percentage = (
            monthly_expenses / budget_amount
        ) * 100

        budget_remaining = budget_amount - monthly_expenses
    else:
        budget_used_percentage = 0.0
        budget_remaining = 0.0

    spending_alerts = []

    if budget_amount > 0:
        if monthly_expenses >= budget_amount:
            spending_alerts.append(
                "🚨 Budget Exceeded: "
                "You have exceeded your monthly budget."
            )
        elif monthly_expenses >= budget_amount * 0.90:
            spending_alerts.append(
                "🔴 Budget Almost Exceeded: "
                "You have used 90% or more of your budget."
            )
        elif monthly_expenses >= budget_amount * 0.80:
            spending_alerts.append(
                "⚠️ Budget Warning: "
                "You have used 80% or more of your budget."
            )
        else:
            spending_alerts.append(
                "✅ Budget Status: "
                "Your spending is within the budget."
            )
    else:
        spending_alerts.append(
            "ℹ️ No budget set for this month."
        )

    if monthly_income > 0:
        if monthly_expenses > monthly_income:
            spending_alerts.append(
                "🚨 Spending Alert: "
                "Your expenses are higher than your income this month."
            )
        elif monthly_expenses >= monthly_income * 0.90:
            spending_alerts.append(
                "⚠️ Income Alert: "
                "Your expenses are close to your income."
            )
        else:
            spending_alerts.append(
                "✅ Income Status: "
                "Your expenses are below your income."
            )
    else:
        spending_alerts.append(
            "ℹ️ No income recorded for this month."
        )

    category_totals = {}

    for transaction in monthly_transactions:
        if transaction.type != "expense":
            continue

        category = transaction.category
        category_totals[category] = (
            category_totals.get(category, 0.0)
            + float(transaction.amount)
        )

    highest_category = None
    highest_category_amount = 0.0
    highest_category_percentage = 0.0

    if category_totals:
        highest_category = max(
            category_totals,
            key=category_totals.get,
        )

        highest_category_amount = category_totals[highest_category]

        if monthly_expenses > 0:
            highest_category_percentage = (
                highest_category_amount / monthly_expenses
            ) * 100

    if highest_category:
        if highest_category_percentage >= 60:
            spending_alerts.append(
                f"🚨 High Category Spending: {highest_category} "
                f"represents {highest_category_percentage:.1f}% "
                "of your expenses."
            )
        elif highest_category_percentage >= 40:
            spending_alerts.append(
                f"⚠️ Category Alert: {highest_category} "
                f"represents {highest_category_percentage:.1f}% "
                "of your expenses."
            )

    if monthly_income > 0:
        savings_rate = (
            monthly_savings / monthly_income
        ) * 100

        if savings_rate >= 20:
            spending_alerts.append(
                f"💚 Great Savings: You saved {savings_rate:.1f}% "
                "of your income this month."
            )
        elif savings_rate > 0:
            spending_alerts.append(
                f"💡 Savings Tip: Your current savings rate is "
                f"{savings_rate:.1f}%."
            )
        else:
            spending_alerts.append(
                "⚠️ Savings Alert: "
                "You currently have no savings this month."
            )

    recent_transactions = transactions[:5]

    return render_template(
        "transactions/dashboard.html",
        transactions=transactions,
        total_income=total_income,
        total_expenses=total_expenses,
        balance=balance,
        monthly_transactions=monthly_transactions,
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        monthly_savings=monthly_savings,
        current_budget=current_budget,
        budget_amount=budget_amount,
        budget_used_percentage=budget_used_percentage,
        budget_remaining=budget_remaining,
        spending_alerts=spending_alerts,
        recent_transactions=recent_transactions,
        highest_category=highest_category,
        highest_category_amount=highest_category_amount,
        highest_category_percentage=highest_category_percentage,
    )


@transactions_bp.route("/")
@login_required
def list_transactions():
    transactions = (
        Transaction.query
        .filter_by(user_id=current_user.id)
        .order_by(Transaction.date.desc(), Transaction.id.desc())
        .all()
    )

    delete_form = DeleteForm()

    return render_template(
        "transactions/list.html",
        transactions=transactions,
        delete_form=delete_form,
    )


@transactions_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_transaction():
    form = TransactionForm()

    if form.validate_on_submit():
        transaction = Transaction(
            user_id=current_user.id,
            amount=form.amount.data,
            type=form.type.data,
            category=form.category.data,
            description=form.description.data,
            date=form.date.data,
        )

        db.session.add(transaction)
        db.session.commit()

        flash("Transaction added successfully.", "success")

        return redirect(
            url_for("transactions.list_transactions")
        )

    return render_template(
        "transactions/add.html",
        form=form,
    )


@transactions_bp.route(
    "/edit/<int:transaction_id>",
    methods=["GET", "POST"],
)
@login_required
def edit_transaction(transaction_id):
    transaction = (
        Transaction.query
        .filter_by(
            id=transaction_id,
            user_id=current_user.id,
        )
        .first_or_404()
    )

    form = TransactionForm(obj=transaction)

    if form.validate_on_submit():
        transaction.amount = form.amount.data
        transaction.type = form.type.data
        transaction.category = form.category.data
        transaction.description = form.description.data
        transaction.date = form.date.data

        db.session.commit()

        flash("Transaction updated successfully.", "success")

        return redirect(
            url_for("transactions.list_transactions")
        )

    return render_template(
        "transactions/edit.html",
        form=form,
        transaction=transaction,
    )


@transactions_bp.route(
    "/delete/<int:transaction_id>",
    methods=["POST"],
)
@login_required
def delete_transaction(transaction_id):
    # Validate the CSRF token from the delete form.
    form = DeleteForm()

    if not form.validate_on_submit():
        flash(
            "Unable to delete transaction. Please try again.",
            "error",
        )
        return redirect(
            url_for("transactions.list_transactions")
        )

    transaction = (
        Transaction.query
        .filter_by(
            id=transaction_id,
            user_id=current_user.id,
        )
        .first_or_404()
    )

    db.session.delete(transaction)
    db.session.commit()

    flash("Transaction deleted successfully.", "success")

    return redirect(
        url_for("transactions.list_transactions")
    )


@transactions_bp.route("/export")
@login_required
def export_transactions():
    transactions = (
        Transaction.query
        .filter_by(user_id=current_user.id)
        .order_by(Transaction.date.desc())
        .all()
    )

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(
        [
            "Date",
            "Type",
            "Category",
            "Amount",
            "Description",
        ]
    )

    for transaction in transactions:
        writer.writerow(
            [
                transaction.date,
                transaction.type,
                transaction.category,
                transaction.amount,
                transaction.description or "",
            ]
        )

    response = Response(
        output.getvalue(),
        mimetype="text/csv",
    )

    response.headers["Content-Disposition"] = (
        "attachment; filename=transactions.csv"
    )

    return response

