"""
Telegram bot entry point with --test mode for offline verification.

Usage:
    uv run bot.py test start        # Test mode, no Telegram connection
    uv run bot.py test help
    uv run bot.py test health
    uv run bot.py test labs
    uv run bot.py test scores lab-04
    uv run bot.py                   # Production mode, connects to Telegram
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from handlers.commands import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)


def handle_message(text: str) -> str:
    """Route a message to the appropriate handler."""
    # Normalize: ensure text starts with /
    if not text.startswith("/"):
        text = "/" + text
    
    if text == "/start":
        return handle_start()
    elif text == "/help":
        return handle_help()
    elif text == "/health":
        return handle_health()
    elif text == "/labs":
        return handle_labs()
    elif text.startswith("/scores"):
        parts = text.split(maxsplit=1)
        lab_name = parts[1] if len(parts) > 1 else ""
        return handle_scores(lab_name)
    else:
        return "Unknown command. Use /help to see available commands."


def run_test_mode(command: str) -> None:
    """Run a command in test mode and print result to stdout."""
    response = handle_message("/" + command)
    print(response)


def run_production_mode() -> None:
    """Start the Telegram bot (not implemented in Task 1)."""
    print("Production mode not implemented yet. Use test mode for now.")
    print("Example: uv run bot.py test start")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    subparsers = parser.add_subparsers(dest="mode", help="Run mode")
    
    # Test subcommand
    test_parser = subparsers.add_parser("test", help="Run in test mode")
    test_parser.add_argument("command", nargs="+", help="Command to test")
    
    args = parser.parse_args()
    
    if args.mode == "test":
        # Join multi-word commands like "scores lab-04"
        command = " ".join(args.command)
        run_test_mode(command)
    else:
        run_production_mode()


if __name__ == "__main__":
    main()
