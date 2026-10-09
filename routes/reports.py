from datetime import date

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from extensions import db
from models import Transaction, Budget


reports_bp = Blueprint(
    "reports",
    __name__,
    url_prefix="/reports"
)


@reports_bp.route("/")
@login_required
def reports():
    """Display expense report and smart spending insights."""

    today = date.today()

    # =========================================
    # SELECTED MONTH AND YEAR
    # =========================================

    selected_month = request.args.get(
        "month",
        default=today.month,
        type=int
    )

    selected_year = request.args.get(
        "year",
        default=today.year,
        type=int
    )

    if selected_month < 1 or selected_month > 12:
        selected_month = today.month

    if selected_year < 2020 or selected_year > 2100:
        selected_year = today.year

    # =========================================
    # MONTH NAME
    # =========================================

    selected_date = date(
        selected_year,
        selected_month,
        1
    )

    month_name = selected_date.strftime("%B")

    # =========================================
    # TRANSACTIONS FOR SELECTED MONTH
    # =========================================

    transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        db.extract("month", Transaction.date) == selected_month,
        db.extract("year", Transaction.date) == selected_year
    ).all()

    # =========================================
    # CATEGORY-WISE EXPENSES
    # =========================================

    category_expenses = {}

    for transaction in transactions:

        if transaction.type != "expense":
            continue

        category = transaction.category

        if category not in category_expenses:
            category_expenses[category] = 0.0

        # Convert Decimal to float
        category_expenses[category] += float(
            transaction.amount
        )

    category_expenses = dict(
        sorted(
            category_expenses.items(),
            key=lambda item: item[1],
            reverse=True
        )
    )

    # =========================================
    # TOTAL EXPENSES
    # =========================================

    total_expenses = sum(
        category_expenses.values()
    )

    # Make sure total_expenses is always float
    total_expenses = float(total_expenses)

    # =========================================
    # TOTAL INCOME
    # =========================================

    total_income = sum(
        float(transaction.amount)
        for transaction in transactions
        if transaction.type == "income"
    )

    # Make sure total_income is always float
    total_income = float(total_income)

    # =========================================
    # BALANCE / SAVINGS
    # =========================================

    balance = total_income - total_expenses

    # Make sure balance is float
    balance = float(balance)

    # =========================================
    # SAVINGS RATE
    # =========================================

    if total_income > 0:

        savings_rate = (
            balance / total_income
        ) * 100

    else:

        savings_rate = 0.0

    savings_rate = float(savings_rate)

    savings_progress = max(
        0.0,
        min(100.0, savings_rate)
    )

    # =========================================
    # SAVINGS STATUS
    # =========================================

    if total_income <= 0:

        savings_status = "No income recorded"
        savings_status_class = "savings-neutral"

    elif balance <= 0:

        savings_status = "No savings"
        savings_status_class = "savings-danger"

    elif savings_rate < 20:

        savings_status = "Low savings"
        savings_status_class = "savings-warning"

    elif savings_rate < 40:

        savings_status = "Good savings"
        savings_status_class = "savings-good"

    else:

        savings_status = "Excellent savings"
        savings_status_class = "savings-excellent"

    # =========================================
    # MONTHLY SPENDING TREND
    # =========================================

    year_transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        db.extract("year", Transaction.date) == selected_year
    ).all()

    monthly_expenses = [0.0] * 12

    for transaction in year_transactions:

        if transaction.type != "expense":
            continue

        month_index = transaction.date.month - 1

        monthly_expenses[month_index] += float(
            transaction.amount
        )

    monthly_labels = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December"
    ]

    # =========================================
    # BUDGET
    # =========================================

    budget = Budget.query.filter_by(
        user_id=current_user.id,
        month=selected_month,
        year=selected_year
    ).first()

    if budget:

        budget_amount = float(
            budget.amount
        )

    else:

        budget_amount = 0.0

    # =========================================
    # BUDGET REMAINING
    # =========================================

    budget_remaining = (
        budget_amount
        - total_expenses
    )

    budget_remaining = float(budget_remaining)

    # =========================================
    # BUDGET USED PERCENTAGE
    # =========================================

    if budget_amount > 0:

        budget_used_percentage = (
            total_expenses
            / budget_amount
        ) * 100

    else:

        budget_used_percentage = 0.0

    budget_used_percentage = float(
        budget_used_percentage
    )

    budget_progress = max(
        0.0,
        min(100.0, budget_used_percentage)
    )

    # =========================================
    # BUDGET STATUS
    # =========================================

    if budget_amount <= 0:

        budget_status = "No budget set"
        budget_status_class = "budget-neutral"

    elif budget_used_percentage >= 100:

        budget_status = "Budget exceeded"
        budget_status_class = "budget-danger"

    elif budget_used_percentage >= 80:

        budget_status = "Approaching budget limit"
        budget_status_class = "budget-warning"

    else:

        budget_status = "Within budget"
        budget_status_class = "budget-safe"

    # =========================================
    # SMART SPENDING INSIGHTS
    # =========================================

    smart_insights = []

    # -----------------------------------------
    # Insight 1: Highest spending category
    # -----------------------------------------

    highest_category = None
    highest_category_amount = 0.0
    highest_category_percentage = 0.0

    if category_expenses:

        highest_category = next(
            iter(category_expenses)
        )

        highest_category_amount = float(
            category_expenses[highest_category]
        )

        if total_expenses > 0:

            highest_category_percentage = (
                highest_category_amount
                / total_expenses
            ) * 100

        smart_insights.append(
            f"Your highest spending category is "
            f"{highest_category}, accounting for "
            f"{highest_category_percentage:.1f}% "
            f"of your expenses."
        )

    # -----------------------------------------
    # Insight 2: Budget usage
    # -----------------------------------------

    if budget_amount > 0:

        if budget_used_percentage >= 100:

            smart_insights.append(
                "You have exceeded your monthly "
                "budget. Consider reducing "
                "non-essential spending."
            )

        elif budget_used_percentage >= 80:

            smart_insights.append(
                f"You have used "
                f"{budget_used_percentage:.1f}% "
                f"of your budget. You are getting "
                f"close to your monthly limit."
            )

        else:

            smart_insights.append(
                f"You have used "
                f"{budget_used_percentage:.1f}% "
                f"of your budget. Your spending "
                f"is currently within the limit."
            )

    else:

        smart_insights.append(
            "No budget is set for this month. "
            "Setting a budget can help you "
            "control your spending."
        )

    # -----------------------------------------
    # Insight 3: Savings
    # -----------------------------------------

    if total_income > 0:

        if balance > 0:

            smart_insights.append(
                f"You are saving "
                f"{savings_rate:.1f}% of your income "
                f"this month."
            )

        elif balance == 0:

            smart_insights.append(
                "Your income and expenses are "
                "currently equal. There is no "
                "remaining balance."
            )

        else:

            smart_insights.append(
                f"Your expenses are "
                f"₹{abs(balance):.2f} higher "
                f"than your income this month."
            )

    else:

        smart_insights.append(
            "Add an income transaction to get "
            "personalized savings insights."
        )

    # -----------------------------------------
    # Insight 4: Spending compared with income
    # -----------------------------------------

    if total_income > 0:

        expense_ratio = (
            total_expenses
            / total_income
        ) * 100

        expense_ratio = float(expense_ratio)

        if expense_ratio >= 100:

            smart_insights.append(
                "Your expenses are equal to or "
                "higher than your income. "
                "Review your largest expenses."
            )

        elif expense_ratio >= 80:

            smart_insights.append(
                f"Your expenses use "
                f"{expense_ratio:.1f}% of your income. "
                "Keeping this ratio lower can "
                "help increase your savings."
            )

        else:

            smart_insights.append(
                f"Your expenses use "
                f"{expense_ratio:.1f}% of your income. "
                "Your income currently covers "
                "your spending."
            )

    # =========================================
    # SMART INSIGHT STATUS
    # =========================================

    if (
        budget_amount > 0
        and budget_used_percentage >= 100
    ):

        insight_status = "Attention needed"
        insight_status_class = "insight-danger"

    elif (
        total_income > 0
        and balance < 0
    ):

        insight_status = "Spending is high"
        insight_status_class = "insight-danger"

    elif (
        budget_amount > 0
        and budget_used_percentage >= 80
    ):

        insight_status = "Keep an eye on spending"
        insight_status_class = "insight-warning"

    elif (
        total_income > 0
        and savings_rate >= 20
    ):

        insight_status = "Good financial progress"
        insight_status_class = "insight-good"

    else:

        insight_status = "Financial overview"
        insight_status_class = "insight-neutral"

    # =========================================
    # FINANCIAL HEALTH SCORE
    # =========================================

    financial_health_score = 50

    # -----------------------------------------
    # Savings score: maximum 35 points
    # -----------------------------------------

    if total_income > 0:

        if savings_rate >= 40:
            savings_score = 35

        elif savings_rate >= 30:
            savings_score = 30

        elif savings_rate >= 20:
            savings_score = 25

        elif savings_rate >= 10:
            savings_score = 15

        elif savings_rate > 0:
            savings_score = 8

        else:
            savings_score = 0

    else:

        savings_score = 0

    # -----------------------------------------
    # Budget score: maximum 30 points
    # -----------------------------------------

    if budget_amount > 0:

        if budget_used_percentage <= 60:
            budget_score = 30

        elif budget_used_percentage <= 80:
            budget_score = 25

        elif budget_used_percentage < 100:
            budget_score = 15

        else:
            budget_score = 0

    else:

        budget_score = 10

    # -----------------------------------------
    # Expense-to-income score: maximum 25
    # points
    # -----------------------------------------

    if total_income > 0:

        expense_ratio = (
            total_expenses
            / total_income
        ) * 100

        if expense_ratio <= 60:
            expense_score = 25

        elif expense_ratio <= 75:
            expense_score = 20

        elif expense_ratio <= 90:
            expense_score = 12

        elif expense_ratio < 100:
            expense_score = 5

        else:
            expense_score = 0

    else:

        expense_score = 0

    # -----------------------------------------
    # Category concentration score: maximum 10
    # points
    # -----------------------------------------

    if highest_category_percentage < 40:

        category_score = 10

    elif highest_category_percentage < 60:

        category_score = 5

    else:

        category_score = 0

    # -----------------------------------------
    # Final score
    # -----------------------------------------

    financial_health_score = (
        savings_score
        + budget_score
        + expense_score
        + category_score
    )

    financial_health_score = max(
        0,
        min(100, financial_health_score)
    )

    # -----------------------------------------
    # Score status
    # -----------------------------------------

    if financial_health_score >= 80:

        financial_health_status = "Excellent"
        financial_health_class = "health-excellent"

    elif financial_health_score >= 60:

        financial_health_status = "Good"
        financial_health_class = "health-good"

    elif financial_health_score >= 40:

        financial_health_status = "Needs Attention"
        financial_health_class = "health-warning"

    else:

        financial_health_status = "Needs Improvement"
        financial_health_class = "health-danger"

    # =========================================
    # SMART RECOMMENDATION
    # =========================================

    if (
        highest_category
        and highest_category_percentage >= 40
    ):

        smart_recommendation = (
            f"Consider reviewing your "
            f"{highest_category} spending because "
            f"it makes up "
            f"{highest_category_percentage:.1f}% "
            f"of your total expenses."
        )

    elif (
        budget_amount > 0
        and budget_used_percentage >= 80
    ):

        smart_recommendation = (
            "Try to limit non-essential purchases "
            "for the rest of the month so you can "
            "stay within your budget."
        )

    elif (
        total_income > 0
        and savings_rate >= 20
    ):

        smart_recommendation = (
            "Your current savings rate is healthy. "
            "Continue monitoring your expenses "
            "and maintaining your budget."
        )

    elif (
        total_income > 0
        and balance <= 0
    ):

        smart_recommendation = (
            "Review your largest expense categories "
            "and look for areas where spending can "
            "be reduced."
        )

    else:

        smart_recommendation = (
            "Continue recording your income and "
            "expenses to receive more useful "
            "spending insights."
        )

    # =========================================
    # RENDER REPORT
    # =========================================

    return render_template(
        "reports.html",

        # Financial health
        financial_health_score=financial_health_score,
        financial_health_status=financial_health_status,
        financial_health_class=financial_health_class,

        # Selected period
        selected_month=selected_month,
        selected_year=selected_year,
        month_name=month_name,

        # Basic totals
        total_income=total_income,
        total_expenses=total_expenses,
        balance=balance,

        # Savings
        savings_rate=savings_rate,
        savings_progress=savings_progress,
        savings_status=savings_status,
        savings_status_class=savings_status_class,

        # Categories
        category_expenses=category_expenses,

        # Monthly trend
        monthly_labels=monthly_labels,
        monthly_expenses=monthly_expenses,

        # Budget
        budget_amount=budget_amount,
        budget_remaining=budget_remaining,
        budget_used_percentage=budget_used_percentage,
        budget_progress=budget_progress,
        budget_status=budget_status,
        budget_status_class=budget_status_class,

        # Smart insights
        smart_insights=smart_insights,
        insight_status=insight_status,
        insight_status_class=insight_status_class,
        smart_recommendation=smart_recommendation,

        # Highest category
        highest_category=highest_category,
        highest_category_amount=highest_category_amount,
        highest_category_percentage=highest_category_percentage
    )