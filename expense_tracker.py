
"""
Expense Tracker 
=====================================
Python program to track expenses/income in a CSV file
and show a monthly summary. Code cosisits below things -

- Input validation (dates, month format, amount)
- Safer error handling with friendly messages
- A simple text menu loop with an "Exit" option

Run:
    python expense_tracker.py

Test:
    pytest -q

"""

from __future__ import annotations

import csv
import re
from datetime import date
from pathlib import Path
from typing import Tuple, List, Dict

# ---- Configuration ----
DATA_FILE = Path("transactions.csv")
ALLOWED_TYPES = {"expense", "income"}
CATEGORIES = [
    "Groceries", "Transport", "Utilities", "Dining", "Entertainment", "Salary", "Other"
]


# ---------------------- Validations  ----------------------

def ensure_file_exists() -> None:
    """Create the CSV file with a header if it doesn't exist.

    This makes the first run smooth—no manual setup required.
    """
    if not DATA_FILE.exists():
        with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "type", "amount", "category", "description"])


def is_valid_date(iso_date: str) -> bool:
    """Return True if *iso_date* looks like YYYY-MM-DD and represents a real date.

    Used Python's built-in parser via ``date.fromisoformat`` to check validity.
    """
    try:
        date.fromisoformat(iso_date)
        return True
    except Exception:
        return False


def is_valid_month(yyyy_mm: str) -> bool:
    """Return True if *yyyy_mm* looks like YYYY-MM and month is between 01..12."""
    if not re.fullmatch(r"\d{4}-\d{2}", yyyy_mm or ""):
        return False
    year, mm = yyyy_mm.split("-")
    try:
        m = int(mm)
        return 1 <= m <= 12
    except ValueError:
        return False


def parse_amount(raw: str) -> float:
    """Convert *raw* string to a non-negative float amount.

    Raises:
        ValueError: if the string is not a number or the value is negative.
    """
    val = float(raw)  # may raise ValueError
    if val < 0:
        raise ValueError("Amount cannot be negative.")
    return round(val, 2)


# ---------------------- Transactions and Summary Functions ----------------------

def add_transaction(tx_date: str, tx_type: str, amount: float, category: str, description: str) -> None:
    """Append a transaction row to the CSV file.

    Args:
        tx_date: ISO date (YYYY-MM-DD).
        tx_type: Either "expense" or "income".
        amount: A non-negative float (rounded to 2 decimals).
        category: One of the simple categories in ``CATEGORIES``.
        description: Free text note.

    Raises:
        ValueError: If any input is invalid.
    """
    # Validate inputs 
    if not is_valid_date(tx_date):
        raise ValueError("Invalid date. Please use YYYY-MM-DD.")
    if tx_type not in ALLOWED_TYPES:
        raise ValueError("Type must be 'expense' or 'income'.")
    if category not in CATEGORIES:
        raise ValueError(f"Unknown category. Choose from: {', '.join(CATEGORIES)}")

    with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([tx_date, tx_type, f"{amount:.2f}", category, description])


def read_transactions() -> List[Dict[str, str]]:
    """Read all transactions from the CSV file as a list of dicts.

    Returns:
        A list where each element is a dict with keys matching the header columns.
    """
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def monthly_summary(month: str) -> Tuple[float, float, float]:
    """Calculate totals for a given month (YYYY-MM).

    Args:
        month: Month in ``YYYY-MM`` format.

    Returns:
        A tuple ``(total_expense, total_income, balance)`` where balance = income - expense.

    Raises:
        ValueError: If *month* is not in ``YYYY-MM`` format.
    """
    if not is_valid_month(month):
        raise ValueError("Invalid month. Please use YYYY-MM.")

    total_expense = 0.0
    total_income = 0.0

    for tx in read_transactions():
        if tx["date"].startswith(month):
            try:
                amount = float(tx["amount"])  # defensive parse
            except Exception:
                # If a bad row exists, skip it politely
                continue
            if tx["type"] == "expense":
                total_expense += amount
            elif tx["type"] == "income":
                total_income += amount

    return round(total_expense, 2), round(total_income, 2), round(total_income - total_expense, 2)


# ---------------------- Simple Text Menu ----------------------

def menu_loop() -> None:
    """Run a small loop to use the app."""
    ensure_file_exists()

    while True:
        print("
Expense Tracker")
        print("1. Add transaction")
        print("2. Monthly summary")
        print("3. Exit")
        choice = input("Choose an option (1/2/3): ").strip()

        if choice == "1":
            try:
                date_str = input("Date (YYYY-MM-DD): ").strip()
                if not is_valid_date(date_str):
                    raise ValueError("Please use YYYY-MM-DD.")

                tx_type = input("Type (expense/income): ").strip().lower()
                if tx_type not in ALLOWED_TYPES:
                    raise ValueError("Type must be 'expense' or 'income'.")

                amount = parse_amount(input("Amount: ").strip())

                print("Categories:", ", ".join(CATEGORIES))
                category = input("Category: ").strip()
                if category not in CATEGORIES:
                    raise ValueError(f"Unknown category. Choose from: {', '.join(CATEGORIES)}")

                description = input("Description: ").strip()

                add_transaction(date_str, tx_type, amount, category, description)
                print("✅ Transaction added!")
            except ValueError as e:
                print(f"❌ {e}")
            except Exception:
                print("❌ Something went wrong while adding the transaction.")

        elif choice == "2":
            month = input("Enter month (YYYY-MM): ").strip()
            try:
                expense, income, balance = monthly_summary(month)
                print("
--- Summary ---")
                print(f"Total Expense: {expense}")
                print(f"Total Income:  {income}")
                print(f"Balance:       {balance}")
            except ValueError as e:
                print(f"❌ {e}")

        elif choice == "3":
            print("Goodbye! 👋")
            break
        else:
            print("Please choose 1, 2, or 3.")


def main() -> None:
    """Entry point when running the script directly."""
    menu_loop()


if __name__ == "__main__":
    main()
