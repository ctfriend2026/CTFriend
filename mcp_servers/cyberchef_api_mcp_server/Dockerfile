# CyberChef API MCP adapter container.
# Builds the Python FastMCP service that exposes CyberChef operations to CTFriend.
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

# Compile bytecode during sync and copy packages into a portable virtualenv.
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
# Use the Python already present in the base image.
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Copy all files so uv can resolve project metadata such as README.md.
ADD . /app

# Install locked production dependencies only.
RUN uv sync --frozen --no-dev --no-editable

# Final runtime image contains the synced app but not uv builder tooling.
FROM python:3.13-slim-bookworm
COPY --from=builder --chown=app:app /app /app
# Put the project virtualenv first on PATH.
ENV PATH="/app/.venv/bin:$PATH"
# FastMCP reads this port when exposing the API adapter.
ENV FASTMCP_PORT=8001

# Run the MCP server module directly.
CMD ["python", "/app/src/__main__.py"]
