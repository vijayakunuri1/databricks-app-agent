#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-dev}"

echo "Validating bundle..."
databricks bundle validate

echo "Deploying to target: ${TARGET}..."
databricks bundle deploy -t "${TARGET}"

echo "Starting app on target: ${TARGET}..."
databricks bundle run uc_api_app -t "${TARGET}"

echo "Done. Check status with:"
echo "  databricks bundle summary -t ${TARGET}"
