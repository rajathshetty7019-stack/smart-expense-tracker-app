from datetime import datetime

from extensions import db


class Budget(db.Model):
    """Monthly budget model."""

    __tablename__ = "budgets"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    month = db.Column(
        db.Integer,
        nullable=False
    )

    year = db.Column(
        db.Integer,
        nullable=False
    )

    amount = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "budgets",
            lazy=True
        )
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "month",
            "year",
            name="unique_user_month_budget"
        ),
    )

    def __repr__(self):
        return (
            f"<Budget {self.user_id}: "
            f"{self.month}/{self.year} "
            f"{self.amount}>"
        )