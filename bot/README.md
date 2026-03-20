# LMS Telegram Bot

Telegram bot for interacting with the LMS backend.

## Usage

### Test mode

```bash
uv run bot.py test start
uv run bot.py test help
uv run bot.py test health
uv run bot.py test labs
uv run bot.py test scores lab-04
```

### Production mode

```bash
uv run bot.py
```

## Configuration

Create `.env.bot.secret` with:

```
BOT_TOKEN=your-telegram-bot-token
LMS_API_URL=http://localhost:42002
LMS_API_KEY=your-api-key
LLM_API_KEY=your-llm-api-key
```
