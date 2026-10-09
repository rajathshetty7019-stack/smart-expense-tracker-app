
import calendar
from datetime import date

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    url_for,
)
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import (
    DecimalField,
    DateField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, NumberRange, Length, Optional
from sqlalchemy.exc import IntegrityError

from extensions import db
from models.transaction import Transaction
from models.recurring_transaction import (
    RecurringTransaction,
    RecurringTransactionOccurrence,
)


recurring_bp = Blueprint(
    "recurring",
    __name__,
    url_prefix="/recurring",
)


class RecurringTransactionForm(FlaskForm):
    amount = DecimalField(
        "Amount",
        validators=[
            DataRequired(),
            NumberRange(min=0.01, message="Amount must be greater than zero."),
        ],
        places=2,
    )

    type = SelectField(
        "Type",
        choices=[
            ("expense", "Expense"),
            ("income", "Income"),
        ],
        validators=[DataRequired()],
    )

    category = StringField(
        "Category",
        validators=[DataRequired(), Length(max=50)],
    )

    description = StringField(
        "Description",
        validators=[Optional(), Length(max=255)],
    )

    start_date = DateField(
        "First transaction date",
        default=date.today,
        validators=[DataRequired()],
    )

    submit = SubmitField("Save recurring transaction")


class RecurringActionForm(FlaskForm):
    submit = SubmitField("Confirm")


def monthly_date(year, month, day):
    """Return a valid monthly date, capped at the month's last day."""
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(day, last_day))


def process_due_transactions(user_id):
    """Create missing monthly transactions due on or before today."""
    today = date.today()

    rules = RecurringTransaction.query.filter_by(
        user_id=user_id,
        is_active=True,
    ).all()

    for rule in rules:
        start = rule.start_date

        if start > today:
            continue

        year = start.year
        month = start.month

        while (year, month) <= (today.year, today.month):
            scheduled_date = monthly_date(
                year,
                month,
                rule.day_of_month,
            )

            # The first occurrence cannot be before the rule's start date.
            if scheduled_date >= start and scheduled_date <= today:
                existing = RecurringTransactionOccurrence.query.filter_by(
                    recurring_transaction_id=rule.id,
                    scheduled_for=scheduled_date,
                ).first()

                if existing is None:
                    transaction = Transaction(
                        user_id=rule.user_id,
                        amount=rule.amount,
                        type=rule.type,
                        category=rule.category,
                        description=rule.description,
                        date=scheduled_date,
                    )

                    occurrence = RecurringTransactionOccurrence(
                        recurring_transaction_id=rule.id,
                        scheduled_for=scheduled_date,
                        transaction=transaction,
                    )

                    db.session.add(transaction)
                    db.session.add(occurrence)

                    try:
                        db.session.commit()
                    except IntegrityError:
                        # Protect against duplicate occurrences.
                        db.session.rollback()

            if month == 12:
                year += 1
                month = 1
            else:
                month += 1


@recurring_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    process_due_transactions(current_user.id)

    form = RecurringTransactionForm()

    if form.validate_on_submit():
        start_date = form.start_date.data

        rule = RecurringTransaction(
            user_id=current_user.id,
            amount=form.amount.data,
            type=form.type.data,
            category=form.category.data.strip(),
            description=(form.description.data or "").strip() or None,
            start_date=start_date,
            day_of_month=start_date.day,
            is_active=True,
        )

        db.session.add(rule)
        db.session.commit()

        # Create the first occurrence immediately if it is already due.
        process_due_transactions(current_user.id)

        flash("Recurring transaction saved successfully.", "success")
        return redirect(url_for("recurring.index"))

    rules = RecurringTransaction.query.filter_by(
        user_id=current_user.id
    ).order_by(
        RecurringTransaction.created_at.desc()
    ).all()

    action_form = RecurringActionForm()

    return render_template(
        "recurring/index.html",
        form=form,
        action_form=action_form,
        rules=rules,
    )


@recurring_bp.route("/<int:rule_id>/toggle", methods=["POST"])
@login_required
def toggle(rule_id):
    form = RecurringActionForm()

    if not form.validate_on_submit():
        flash("Please submit the form again.", "error")
        return redirect(url_for("recurring.index"))

    rule = RecurringTransaction.query.filter_by(
        id=rule_id,
        user_id=current_user.id,
    ).first_or_404()

    rule.is_active = not rule.is_active
    db.session.commit()

    status = "resumed" if rule.is_active else "paused"
    flash(f"Recurring transaction {status}.", "success")

    return redirect(url_for("recurring.index"))


@recurring_bp.route("/<int:rule_id>/delete", methods=["POST"])
@login_required
def delete(rule_id):
    form = RecurringActionForm()

    if not form.validate_on_submit():
        flash("Please submit the form again.", "error")
        return redirect(url_for("recurring.index"))

    rule = RecurringTransaction.query.filter_by(
        id=rule_id,
        user_id=current_user.id,
    ).first_or_404()

    db.session.delete(rule)
    db.session.commit()

    flash("Recurring transaction deleted.", "success")
    return redirect(url_for("recurring.index"))