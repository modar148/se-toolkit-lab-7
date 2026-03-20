"""
Configuration loader for the bot.

Loads settings from environment variables, with support for .env files.
"""

from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class BotConfig(BaseSettings):
    """Bot configuration loaded from environment variables."""

    # Telegram bot token (required for production mode)
    bot_token: str = ""

    # LMS Backend API
    lms_api_url: str = "http://localhost:42002"
    lms_api_key: str = ""

    # LLM API (for Task 3 - intent routing)
    llm_api_key: str = ""
    llm_api_base_url: str = ""
    llm_api_model: str = ""
    llm_model: str = "gpt-4o-mini"

    class Config:
        env_file = ".env.bot.secret"
        env_file_encoding = "utf-8"
        extra = "ignore"


def load_config() -> BotConfig:
    """Load configuration from environment or .env file."""
    # Try to load from .env.bot.secret in the bot directory
    env_path = Path(__file__).parent / ".env.bot.secret"
    if env_path.exists():
        load_dotenv(env_path)
    return BotConfig()


# Global config instance
config = load_config()
