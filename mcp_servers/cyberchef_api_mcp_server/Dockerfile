FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Copy all files so uv can see README.md and pyproject.toml
ADD . /app

# Sync dependencies and build the project
RUN uv sync --frozen --no-dev --no-editable

# Final runtime image
FROM python:3.13-slim-bookworm
COPY --from=builder --chown=app:app /app /app
ENV PATH="/app/.venv/bin:$PATH"
ENV FASTMCP_PORT=8001

# Run the Python module directly
CMD ["python", "/app/src/__main__.py"]

