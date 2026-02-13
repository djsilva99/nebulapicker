# Use Python version from .python-version or default to 3.12
ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    DATABASE_URL="postgresql://postgres:postgres@localhost:5432/nebulapicker" \
    WALLABAG_ENABLED=False
    WALLABAG_URL= \
    WALLABAG_CLIENT_ID= \
    WALLABAG_CLIENT_SECRET= \
    WALLABAG_USERNAME= \
    WALLABAG_password=

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libffi-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==2.2.1

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy only dependency files first for caching
COPY pyproject.toml poetry.lock* ./

# Install dependencies without dev packages
RUN poetry install --no-root --without dev --only main

# Copy the application code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
