# Multi-stage build: build frontend with Node, then build Python image serving Flask

# 1) Build frontend
FROM node:20-alpine AS frontend-build
WORKDIR /opt/frontend
COPY frontend/package.json frontend/package-lock.json* ./
COPY frontend/ .
# Use npm install so Docker build works even without package-lock.json
# install full deps (including dev deps needed for the build)
RUN npm install --silent --no-audit --no-fund
RUN npm run build

# 2) Build Python app
FROM python:3.11-slim
WORKDIR /app
# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
# Copy backend
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
# Copy built frontend assets
RUN rm -rf frontend && mkdir frontend && cp -r /opt/frontend/dist/* frontend/

ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
