FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the whole repo and then work from backend folder
COPY .. /app
WORKDIR /app/backend

# If you have a requirements.txt here (or adjust path if different)
RUN if [ -f requirements.txt ]; then \
      pip install --no-cache-dir -r requirements.txt; \
    fi

# Default: run FastAPI via uvicorn
# Adjust "app.main:app" and port if your module/path is different.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
