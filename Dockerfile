# Multi-stage build: build frontend with Node, then build Python image serving Flask

# 1) Build frontend
FROM node:20-alpine AS frontend-build
WORKDIR /opt/frontend
COPY frontend/package.json frontend/package-lock.json* ./
COPY frontend/ .
RUN npm install --silent --no-audit --no-fund
RUN npm run build

# 2) Build Python app
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Copy built frontend assets from the frontend build stage
COPY --from=frontend-build /opt/frontend/dist ./frontend

ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]