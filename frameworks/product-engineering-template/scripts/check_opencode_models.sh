#!/usr/bin/env bash
set -euo pipefail

# v10.12 — backward-compat alias for check_models.sh
echo "[v10.12] check_opencode_models.sh is now an alias for check_models.sh"
echo "[v10.12] forwarding with engine=opencode"
exec bash scripts/check_models.sh opencode
