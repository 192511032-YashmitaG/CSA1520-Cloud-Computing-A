#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 scripts/platform_audit.py
python3 scripts/analytical_model.py
echo "Done. Review generated files in results/."
