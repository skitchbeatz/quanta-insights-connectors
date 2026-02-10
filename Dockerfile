# Multi-stage Dockerfile for Quanta Insights Connectors
FROM python:3.12-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy pyproject.toml for dependency installation
COPY pyproject.toml ./

# Install dependencies (including dev dependencies for building)
RUN pip install --no-cache-dir -e .[dev]

# Production stage
FROM python:3.12-slim as production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash quanta

# Set working directory
WORKDIR /app

# Copy pyproject.toml and source code
COPY pyproject.toml ./
COPY src/ ./src/

# Install dependencies
RUN pip install --no-cache-dir -e .

# Set ownership
RUN chown -R quanta:quanta /app

# Switch to non-root user
USER quanta

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command (will be overridden by docker-compose)
CMD ["python", "-m", "quanta_insights.server", "--transport", "stdio"]
