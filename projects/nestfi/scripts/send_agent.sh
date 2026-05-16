#!/usr/bin/env bash
set -euo pipefail

# v10 — compatibility alias only. Prefer scripts/route_to_pane.sh.
echo "[v10] send_agent.sh is a compatibility alias — forwarding to scripts/route_to_pane.sh"
exec bash scripts/route_to_pane.sh "$@"
