FROM python:3.13-slim-bookworm

# Set environment variables for faster, cleaner installs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SENTENCE_TRANSFORMERS_HOME=/app/models

# Create and switch to non-root user
RUN useradd -m app
USER app
WORKDIR /app

# Copy only dependency files first for caching
COPY --chown=app:app pyproject.toml ./

# Install build tools temporarily, then install project dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir .

# Copy rest of the source code
COPY --chown=app:app . /app

# Run your main entrypoint
CMD ["python", "/app/src/__main__.py"]
