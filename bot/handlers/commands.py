"""
Command handlers - pure functions that take input and return text.

These handlers have NO dependency on Telegram. They can be called from:
- --test mode (CLI)
- Unit tests
- Telegram bot (production)
"""

from services.lms_api import lms_client


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
    result = lms_client.get_health()
    if result["healthy"]:
        return f"Backend is healthy. {result.get('item_count', 0)} items available."
    else:
        return f"Backend error: {result.get('error', 'unknown error')}"


def handle_labs() -> str:
    """Handle /labs command - list available labs."""
    result = lms_client.get_labs()
    if "error" in result:
        return f"Error fetching labs: {result['error']}"
    
    labs = result.get("labs", [])
    if not labs:
        return "No labs available."
    
    lines = ["Available labs:"]
    for lab in labs:
        if isinstance(lab, dict):
            name = lab.get("name", lab.get("id", "Unknown"))
            lines.append(f"- {name}")
        else:
            lines.append(f"- {lab}")
    
    return "\n".join(lines)


def handle_scores(lab_name: str = "") -> str:
    """Handle /scores command - show scores for a lab."""
    if not lab_name:
        return "Usage: /scores <lab-name>\nExample: /scores lab-04"
    
    result = lms_client.get_scores(lab_name)
    if "error" in result:
        return f"Error: {result['error']}"
    
    scores = result.get("scores", [])
    if not scores:
        return f"No scores found for {lab_name}."
    
    lines = [f"Pass rates for {lab_name}:"]
    for score in scores:
        if isinstance(score, dict):
            task = score.get("task", score.get("name", "Unknown"))
            rate = score.get("pass_rate", score.get("rate", 0))
            attempts = score.get("attempts", 0)
            lines.append(f"- {task}: {rate:.1f}% ({attempts} attempts)")
        else:
            lines.append(f"- {score}")
    
    return "\n".join(lines)
