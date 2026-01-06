"""Helper utility functions."""
from datetime import datetime


def format_currency(amount):
    """Format amount as currency."""
    return f"₹ {amount:,.2f}"


def format_date(date):
    """Format date for display."""
    if isinstance(date, datetime):
        return date.strftime("%d/%m/%Y")
    return str(date)


def parse_float(value_str):
    """Parse float from string, handling currency symbols."""
    if isinstance(value_str, (int, float)):
        return float(value_str)
    
    # Remove currency symbols and commas
    cleaned = value_str.replace("₹", "").replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0
