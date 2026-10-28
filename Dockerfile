FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY src/ ./src/
RUN uv sync --locked --no-dev

EXPOSE 8000

CMD ["/app/.venv/bin/uvicorn", "scanner_data.app:app", "--host", "0.0.0.0", "--port", "8000"]