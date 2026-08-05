# RAG MCP server container.
# Builds the local knowledge-base retrieval service used by CTFriend MCP tools.
FROM python:3.13-slim-bookworm

# Avoid bytecode writes, stream logs immediately, and keep model caches inside /app.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SENTENCE_TRANSFORMERS_HOME=/app/models

# Create the runtime user and prepare the application directory.
RUN useradd -m app && mkdir -p /app && chown app:app /app
WORKDIR /app

# Copy only dependency files first so dependency installation remains cacheable.
COPY --chown=app:app pyproject.toml ./

# Install project dependencies before switching to the runtime user.
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir .

# Copy the server source code and local package files.
COPY --chown=app:app . /app

# Prepare model/cache paths that the runtime user may write to.
RUN mkdir -p /app/models && chown -R app:app /app

# Switch to the non-root runtime user.
USER app

# Start the FastMCP RAG server.
CMD ["python", "/app/src/__main__.py"]
