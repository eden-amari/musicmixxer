# ------------------------------
# Base image (match uv.lock)
# ------------------------------
FROM python:3.11-slim

# ------------------------------
# UTF + Python settings
# ------------------------------
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# ------------------------------
# System deps
# ------------------------------
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------
# Install uv
# ------------------------------
RUN pip install uv

# ------------------------------
# Workdir
# ------------------------------
WORKDIR /app

# ------------------------------
# Copy dependency files
# ------------------------------
COPY pyproject.toml uv.lock ./

# ------------------------------
# Install dependencies
# ------------------------------
RUN uv sync --frozen

# ------------------------------
# Copy project
# ------------------------------
COPY . .

# ------------------------------
# Expose port
# ------------------------------
EXPOSE 8000

# ------------------------------
# Start (🔥 AUTO MIGRATIONS)
# ------------------------------
CMD ["sh", "-c", "uv run python manage.py migrate && uv run python manage.py runserver 0.0.0.0:8000"]