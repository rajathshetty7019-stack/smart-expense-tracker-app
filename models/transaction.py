from datetime import datetime

from extensions import db


class Transaction(db.Model):
    """Transaction model for income and expenses."""

    __tablename__ = "transactions"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    amount = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    type = db.Column(
        db.String(20),
        nullable=False
    )

    category = db.Column(
        db.String(50),
        nullable=False
    )

    description = db.Column(
        db.String(255),
        nullable=True
    )

    date = db.Column(
        db.Date,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "transactions",
            lazy=True
        )
    )

    def __repr__(self):
        return f"<Transaction {self.id}: {self.type} {self.amount}>"