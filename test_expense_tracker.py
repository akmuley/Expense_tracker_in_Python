
"""Basic tests for the beginner Expense Tracker (Version 3).

These tests are intentionally small and readable—perfect for junior portfolios.
"""
import expense_tracker as et
import csv


def test_monthly_summary_normal(tmp_path, monkeypatch):
    # Point the program to a temp CSV file
    test_file = tmp_path / "transactions.csv"
    monkeypatch.setattr(et, "DATA_FILE", test_file)

    et.ensure_file_exists()
    et.add_transaction("2026-01-01", "expense", 10.0, "Groceries", "Milk")
    et.add_transaction("2026-01-02", "income", 100.0, "Salary", "Pay")

    expense, income, balance = et.monthly_summary("2026-01")

    assert expense == 10.0
    assert income == 100.0
    assert balance == 90.0


def test_monthly_summary_empty_file(tmp_path, monkeypatch):
    test_file = tmp_path / "transactions.csv"
    monkeypatch.setattr(et, "DATA_FILE", test_file)

    et.ensure_file_exists()
    expense, income, balance = et.monthly_summary("2026-01")
    assert expense == 0.0
    assert income == 0.0
    assert balance == 0.0


def test_invalid_month_format_raises(tmp_path, monkeypatch):
    test_file = tmp_path / "transactions.csv"
    monkeypatch.setattr(et, "DATA_FILE", test_file)

    et.ensure_file_exists()
    # Wrong format should raise a ValueError
    import pytest
    with pytest.raises(ValueError):
        et.monthly_summary("202601")  # missing dash


def test_defensive_skip_bad_rows(tmp_path, monkeypatch):
    # If a corrupted amount sneaks into the CSV, the code should skip it (not crash)
    test_file = tmp_path / "transactions.csv"
    monkeypatch.setattr(et, "DATA_FILE", test_file)

    et.ensure_file_exists()

    # Manually write a bad row
    with open(test_file, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["2026-01-01", "expense", "not_a_number", "Groceries", "bad row"])
        w.writerow(["2026-01-02", "income", "100.00", "Salary", "ok row"])

    expense, income, balance = et.monthly_summary("2026-01")
    # bad expense row is skipped, income still counted
    assert expense == 0.0
    assert income == 100.0
    assert balance == 100.0
