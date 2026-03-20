# Bot Development Plan

This document outlines the approach for building the LMS Telegram bot across four tasks.

## Task 1: Plan and Scaffold

**Goal:** Create project structure with testable handler architecture.

**Approach:**
- Separate handlers from Telegram transport layer — handlers are pure functions that take input and return text
- Implement `--test` mode (via `bot.py test <command>`) that calls handlers directly without Telegram
- Create `handlers/` directory for command logic, `services/` for API clients, `config.py` for environment loading
- Use `pyproject.toml` with `uv` for dependency management (not `requirements.txt`)

**Why this architecture:** Testable handlers mean we can verify logic from CLI, write unit tests, and later plug into Telegram — same code, different entry points. This is *separation of concerns*.

## Task 2: Backend Integration

**Goal:** Connect slash commands to real LMS backend data.

**Approach:**
- Create `services/lms_api.py` — HTTP client for backend calls with Bearer token auth
- Update handlers to call API endpoints: `/health` → GET `/items`, `/labs` → list labs, `/scores` → analytics
- Handle errors gracefully — backend down shows friendly message, not crash
- All URLs/keys from environment (`.env.bot.secret`), never hardcoded

**Pattern:** API client abstraction — handlers call `lms_api.get_health()`, not raw HTTP. Makes testing easier.

## Task 3: Intent-Based Natural Language Routing

**Goal:** Let users ask questions in plain English, not just slash commands.

**Approach:**
- Create `services/llm_client.py` — wraps LLM API for intent classification
- Define tools for each backend action (get_health, list_labs, get_scores, etc.) with clear descriptions
- Build intent router: user text → LLM → tool selection → API call → response
- LLM decides which tool to call based on descriptions — no regex matching

**Key insight:** Tool description quality matters more than prompt engineering. Vague descriptions = wrong tool calls.

## Task 4: Containerize and Deploy

**Goal:** Run bot on VM alongside backend via Docker Compose.

**Approach:**
- Create `bot/Dockerfile` — Python slim image, copy bot/, run with `uv`
- Add bot service to `docker-compose.yml` — depends on backend, uses service names for networking
- Document deployment in README — how to start, check logs, update
- Verify bot responds in Telegram after deployment

**Docker networking:** Containers talk via service names (`backend`, not `localhost`). Critical for inter-container HTTP.

## Testing Strategy

- **Test mode:** `bot.py test <command>` for quick verification during development
- **Unit tests:** Test handlers directly (future enhancement)
- **Integration:** Deploy to VM, test in real Telegram

## File Structure

```
bot/
├── bot.py              # Entry point with test mode
├── config.py           # Environment loading
├── pyproject.toml      # Dependencies
├── handlers/
│   ├── __init__.py
│   └── commands.py     # /start, /help, /health, /labs, /scores
└── services/           # (Tasks 2-3)
    ├── lms_api.py      # Backend HTTP client
    └── llm_client.py   # LLM intent router
```
