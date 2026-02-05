FROM python:3.13-slim

WORKDIR /app

# Install system deps if needed (psycopg2 requires gcc + libpq)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency definitions first for Docker caching
COPY pyproject.toml poetry.lock* /app/

# Upgrade pip and install only runtime dependencies
RUN pip install --upgrade pip && \
    pip install . --no-cache-dir

# Copy the source code
COPY . /app

# Copy Streamlit production config
COPY .streamlit /app/.streamlit

# Set sensible defaults for production
ENV MAX_MESSAGES=100 \
    LOG_LEVEL=INFO \
    PYTHONUNBUFFERED=1

# Expose Streamlit port
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "app/__main__.py", \
     "--server.port=8501", \
     "--server.headless=true", \
     "--server.baseUrlPath=ctfriend"]
