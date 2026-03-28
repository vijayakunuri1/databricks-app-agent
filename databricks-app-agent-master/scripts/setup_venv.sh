#!/usr/bin/env bash
set -euo pipefail

VENV_DIR="${1:-.venv}"

echo "Creating virtual environment in ${VENV_DIR}..."
python3 -m venv "${VENV_DIR}"

echo "Activating and installing dependencies..."
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

pip install --upgrade pip
pip install -e ".[dev]"

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example — fill in your credentials."
fi

echo ""
echo "Done. Activate your environment with:"
echo "  source ${VENV_DIR}/bin/activate"
echo ""
echo "Then run the API locally with:"
echo "  uvicorn app:app --reload"
