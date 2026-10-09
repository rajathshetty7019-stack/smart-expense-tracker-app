# Smart Expense Tracker 💰

A personal finance management web application built with **Python and Flask** to help users track income and expenses, manage budgets, schedule recurring transactions, and monitor their financial health.

## ✨ Features

* **User Authentication** — Register and log in to your account.
* **Transaction Management** — Add, edit, delete, and view income and expenses.
* **Dashboard** — Get an overview of your financial activity.
* **Budget Management** — Set budgets and monitor spending against limits.
* **Budget Alerts** — Identify when spending approaches or exceeds budget limits.
* **Recurring Transactions** — Manage repeating financial transactions automatically.
* **Financial Reports** — Review expenses by category and analyze monthly activity.
* **Financial Health Score** — View an overview of your financial habits.
* **Monthly Insights** — Explore budget and savings insights.

## 🛠️ Tech Stack

* **Language:** Python
* **Backend:** Flask
* **Database:** SQLAlchemy with a configured database
* **Frontend:** HTML, CSS, Jinja2 templates
* **Authentication and Forms:** Flask-Login, Flask-WTF
* **Scheduled Tasks:** APScheduler

## 📁 Project Structure

```text
smart-expense-tracker/
├── app.py
├── config.py
├── extensions.py
├── requirements.txt
├── models/
│   ├── user.py
│   ├── transaction.py
│   ├── budget.py
│   └── recurring_transaction.py
├── routes/
│   ├── auth.py
│   ├── transactions.py
│   ├── budget.py
│   ├── recurring.py
│   └── reports.py
├── static/
│   └── style.css
└── templates/
    ├── base.html
    ├── login.html
    ├── register.html
    ├── budget.html
    ├── reports.html
    ├── recurring/
    └── transactions/
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/rajathshetty7019-stack/smart-expense-tracker-app.git
cd smart-expense-tracker-app
```

### 2. Create a virtual environment

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the application

Review `config.py` and configure the required environment variables and database settings according to your local setup. Do not commit passwords, secret keys, or personal database files.

### 5. Run the application

```bash
python app.py
```

Open the local address shown in your terminal in your web browser. The exact address depends on your Flask configuration.

## 🔒 Security Notes

* Never commit secret keys, passwords, or environment files.
* Keep local database files and personal financial records out of version control.
* Use a strong secret key and secure configuration for any deployed instance.
* Use a production-ready server and appropriate security settings before deploying publicly.

## 🚀 Future Improvements

* Interactive charts and visual analytics
* Exportable financial reports
* Savings goals and reminders
* Automated testing and continuous integration
* Cloud deployment

## 👨‍💻 Author

**Rajath Shetty**

GitHub: [@rajathshetty7019-stack](https://github.com/rajathshetty7019-stack)

## 📄 License

No license has been selected yet. Unless a license is added, the default copyright rules apply to this code. Add an appropriate open-source license if you want to permit others to reuse it.
