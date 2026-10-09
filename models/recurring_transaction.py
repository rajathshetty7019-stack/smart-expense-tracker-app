from datetime import date, datetime

from extensions import db


class RecurringTransaction(db.Model):
    __tablename__ = "recurring_transactions"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    amount = db.Column(
        db.Numeric(10, 2),
        nullable=False,
    )

    type = db.Column(
        db.String(20),
        nullable=False,
    )

    category = db.Column(
        db.String(50),
        nullable=False,
    )

    description = db.Column(
        db.String(255),
        nullable=True,
    )

    start_date = db.Column(
        db.Date,
        nullable=False,
        default=date.today,
    )

    day_of_month = db.Column(
        db.Integer,
        nullable=False,
        default=1,
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "recurring_transactions",
            lazy=True,
        ),
    )

    occurrences = db.relationship(
        "RecurringTransactionOccurrence",
        back_populates="recurring_transaction",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def __repr__(self):
        return (
            f"<RecurringTransaction "
            f"{self.id}: {self.type} {self.amount}>"
        )


class RecurringTransactionOccurrence(db.Model):
    __tablename__ = "recurring_transaction_occurrences"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    recurring_transaction_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "recurring_transactions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    scheduled_for = db.Column(
        db.Date,
        nullable=False,
    )

    transaction_id = db.Column(
        db.Integer,
        db.ForeignKey("transactions.id"),
        nullable=True,
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    recurring_transaction = db.relationship(
        "RecurringTransaction",
        back_populates="occurrences",
    )

    transaction = db.relationship(
        "Transaction",
    )

    __table_args__ = (
        db.UniqueConstraint(
            "recurring_transaction_id",
            "scheduled_for",
            name="unique_recurring_transaction_month",
        ),
    )

    def __repr__(self):
        return (
            f"<RecurringTransactionOccurrence "
            f"{self.recurring_transaction_id}: "
            f"{self.scheduled_for}>"
        )

