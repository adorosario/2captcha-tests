# Use Playwright Python base to support E2E tests out of the box
FROM mcr.microsoft.com/playwright/python:v1.46.0-jammy

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install test dependencies
RUN python -m pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir pytest requests python-dotenv

# Default to bash; docker compose will override/attach TTY
CMD ["/bin/bash"]

