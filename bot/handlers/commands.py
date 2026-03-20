"""
Command handlers - pure functions that take input and return text.

These handlers have NO dependency on Telegram. They can be called from:
- --test mode (CLI)
- Unit tests
- Telegram bot (production)
"""


def handle_start() -> str:
    """Handle /start command - welcome message."""
    return "Welcome! I'm your LMS assistant bot. Use /help to see available commands."


def handle_help() -> str:
    """Handle /help command - list available commands."""
    return (
        "Available commands:\n"
        "/start - Welcome message\n"
        "/help - Show this help\n"
        "/health - Check backend status\n"
        "/labs - List available labs\n"
        "/scores <lab> - View scores for a lab"
    )


def handle_health() -> str:
    """Handle /health command - check backend status."""
    # TODO: Task 2 - call backend API
    return "Backend status: unknown (not implemented yet)"


def handle_labs() -> str:
    """Handle /labs command - list available labs."""
    # TODO: Task 2 - call backend API
    return "Available labs: (not implemented yet)"


def handle_scores(lab_name: str = "") -> str:
    """Handle /scores command - show scores for a lab."""
    # TODO: Task 2 - call backend API
    if lab_name:
        return f"Scores for {lab_name}: (not implemented yet)"
    return "Usage: /scores <lab-name>"
