# ------------------------------
# Base image (stable)
# ------------------------------
FROM python:3.11-bookworm

# ------------------------------
# Python environment settings
# ------------------------------
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# ------------------------------
# System dependencies
# ------------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# ------------------------------
# Install uv
# ------------------------------
RUN pip install --no-cache-dir uv

# ------------------------------
# Set working directory
# ------------------------------
WORKDIR /app

# ------------------------------
# Copy dependency files first (layer caching)
# ------------------------------
COPY pyproject.toml uv.lock ./

# ------------------------------
# Install dependencies
# ------------------------------
RUN uv sync --frozen

# ------------------------------
# Copy project files
# ------------------------------
COPY . .

# ------------------------------
# Expose port
# ------------------------------
EXPOSE 8000

# ------------------------------
# Start application
# ------------------------------
CMD ["sh", "-c", "uv run python manage.py migrate && uv run python manage.py runserver 0.0.0.0:8000"]