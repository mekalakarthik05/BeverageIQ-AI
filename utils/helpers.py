def format_currency(amount: float) -> str:
    """Formats a float as currency."""
    return f"${amount:,.2f}"

def format_percentage(value: float) -> str:
    """Formats a float as percentage."""
    return f"{value:.2f}%"
