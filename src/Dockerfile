# CTFriend web app container.
# Builds the Streamlit chatbot service and serves it under the /ctfriend base path.
FROM python:3.13-slim

# Use /app as the package root for dependency installation and runtime files.
WORKDIR /app

# Install system deps needed by Python packages such as psycopg2.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency definitions first so Docker can cache dependency installation.
COPY pyproject.toml poetry.lock* /app/

# Install the local Python package and runtime dependencies.
RUN pip install --upgrade pip && \
    pip install . --no-cache-dir

# Copy application source after dependency installation.
COPY . /app

# Copy Streamlit production config used by the deployed app.
COPY .streamlit /app/.streamlit

# Set runtime defaults; docker-compose or the host can override these values.
ENV MAX_MESSAGES=100 \
    LOG_LEVEL=INFO \
    PYTHONUNBUFFERED=1

# Expose the Streamlit port from inside the container.
EXPOSE 8501

# Start the Streamlit app behind the /ctfriend route.
CMD ["streamlit", "run", "app/__main__.py", \
     "--server.port=8501", \
     "--server.headless=true", \
     "--server.baseUrlPath=ctfriend"]
