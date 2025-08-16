# Use Playwright Python base to support E2E tests out of the box
FROM python:3.12-slim AS base

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install minimal test dependencies for smoke tests
RUN python -m pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir pytest requests python-dotenv

CMD ["/bin/bash"]

FROM mcr.microsoft.com/playwright/python:v1.46.0-jammy AS e2e

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install E2E deps and browsers (heavy; build only when needed)
RUN python -m pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir pytest requests python-dotenv playwright \
    && python -m playwright install --with-deps chromium

CMD ["/bin/bash"]
