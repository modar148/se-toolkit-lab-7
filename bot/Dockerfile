# Bot Dockerfile
# Uses uv for dependency management (not pip/requirements.txt)

FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files first (for better caching)
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy bot code
COPY . .

# Run the bot
CMD ["uv", "run", "bot.py"]
