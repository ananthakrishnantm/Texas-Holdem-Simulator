FROM python:3.12-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies (no dev deps)
RUN poetry install --no-root --no-interaction --no-ansi --only main

# Copy source code
COPY src ./src

# Let Python know where your source lives
ENV PYTHONPATH=/app/src

# Expose FastAPI port
EXPOSE 8000

# Start app
CMD ["poetry", "run", "uvicorn", "poker_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
