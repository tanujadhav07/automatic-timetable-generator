#!/usr/bin/env bash
set -euo pipefail

VENV_PATH=".venv"

echo "Preparing local run (Unix shell)"

if [ ! -d "$VENV_PATH" ]; then
  python3 -m venv "$VENV_PATH"
fi

echo "Activating venv..."
# shellcheck disable=SC1091
source "$VENV_PATH/bin/activate"

echo "Installing Python requirements..."
pip install -r requirements.txt

echo "Starting Flask app (debug mode). Access http://localhost:5000"
python app.py
