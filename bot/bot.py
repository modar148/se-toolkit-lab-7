"""
Telegram bot entry point with --test mode for offline verification.

Usage:
    uv run bot.py --test "/start"     # Test mode, no Telegram connection
    uv run bot.py --test "/help"
    uv run bot.py --test "/health"
    uv run bot.py --test "/labs"
    uv run bot.py --test "/scores lab-04"
    uv run bot.py test start          # Alternative syntax
    uv run bot.py                     # Production mode, connects to Telegram
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
    handle_natural_language,
)


def handle_message(text: str) -> str:
    """Route a message to the appropriate handler."""
    # Check if it's a command (starts with /)
    if text.startswith("/"):
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
    else:
        # Natural language message - use LLM intent router
        return handle_natural_language(text)


def run_test_mode(command: str) -> None:
    """Run a command in test mode and print result to stdout."""
    # Strip leading / if present to avoid double-slash
    command = command.lstrip("/")
    
    # If it was a command (had /), treat as command
    # Otherwise treat as natural language
    if command.startswith("/"):
        response = handle_message(command)
    else:
        # Natural language - pass directly to handle_message
        response = handle_message(command)
    
    print(response)


def run_production_mode() -> None:
    """Start the Telegram bot."""
    import asyncio
    from aiogram import Bot, Dispatcher, types
    from aiogram.filters import CommandStart, Command
    
    from config import config

    if not config.bot_token:
        print("Error: BOT_TOKEN not set in .env.bot.secret")
        sys.exit(1)

    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def cmd_start(message: types.Message) -> None:
        await message.answer(handle_start())

    @dp.message(Command("help"))
    async def cmd_help(message: types.Message) -> None:
        await message.answer(handle_help())

    @dp.message(Command("health"))
    async def cmd_health(message: types.Message) -> None:
        await message.answer(handle_health())

    @dp.message(Command("labs"))
    async def cmd_labs(message: types.Message) -> None:
        await message.answer(handle_labs())

    @dp.message(Command("scores"))
    async def cmd_scores(message: types.Message) -> None:
        lab_name = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
        await message.answer(handle_scores(lab_name))

    @dp.message()
    async def handle_natural_language_message(message: types.Message) -> None:
        """Handle non-command messages with LLM intent routing."""
        text = message.text
        if text and not text.startswith("/"):
            response = handle_natural_language(text)
            await message.answer(response)

    async def main() -> None:
        print("Bot started...")
        await dp.start_polling(bot)

    asyncio.run(main())


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    
    # Support both --test flag and test subcommand
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Run in test mode with the given command"
    )
    
    # Also support subcommand syntax
    subparsers = parser.add_subparsers(dest="mode", help="Run mode")
    test_parser = subparsers.add_parser("test", help="Run in test mode")
    test_parser.add_argument("command", nargs="+", help="Command to test")

    args = parser.parse_args()

    # Check --test flag first
    if args.test:
        run_test_mode(args.test)
    elif args.mode == "test":
        # Join multi-word commands like "scores lab-04"
        command = " ".join(args.command)
        run_test_mode(command)
    else:
        run_production_mode()


if __name__ == "__main__":
    main()
