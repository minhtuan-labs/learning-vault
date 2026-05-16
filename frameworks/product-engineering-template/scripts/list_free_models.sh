#!/usr/bin/env bash
set -euo pipefail

# v10.16.1 — Discover free models available in the active engine.
#
# Usage:
#   bash scripts/list_free_models.sh [engine]
#
# If `engine` is omitted, reads it from .agent_session. Otherwise
# defaults to opencode.

ENGINE_ARG="${1:-}"

# Strip -free suffix so `list_free_models.sh opencode-free` works as
# the intuitive shorthand. The script doesn't need to source the overlay
# anyway — it just lists what's reachable via `<binary> models`.
if [[ "$ENGINE_ARG" == *-free ]]; then
  ENGINE_ARG="${ENGINE_ARG%-free}"
fi

ENGINE="${ENGINE_ARG:-opencode}"

if [[ -z "$ENGINE_ARG" && -f ".agent_session" ]]; then
  # shellcheck disable=SC1090
  source .agent_session
fi

ENGINE_CFG="config/engines/${ENGINE}.env"
if [[ ! -f "$ENGINE_CFG" ]]; then
  echo "ERROR: engine config not found: $ENGINE_CFG"
  echo "Available engines:"
  ls -1 config/engines/*.env 2>/dev/null | grep -v '\-free\.env$' \
    | sed 's|config/engines/||;s|.env$||' | sed 's/^/  - /'
  exit 1
fi
# shellcheck disable=SC1090
source "$ENGINE_CFG"

echo "================================================================"
echo " Free-tier models available for engine: $ENGINE"
echo "================================================================"

case "$ENGINE" in
  opencode)
    if ! command -v "$ENGINE_BINARY" >/dev/null 2>&1; then
      echo "ERROR: '$ENGINE_BINARY' not in PATH."
      exit 1
    fi

    # opencode-go variant: `opencode models` lists everything. Filter
    # for `:free` suffix (OpenRouter convention) or anything with the
    # word "free" in the line.
    echo
    echo "Models with ':free' suffix (OpenRouter free-tier):"
    echo "----------------------------------------------------------------"
    "$ENGINE_BINARY" models 2>/dev/null | grep -iE ':free($|[[:space:]])' || \
      echo "  (none found — your fork may use a different naming convention)"

    echo
    echo "All models containing the word 'free' anywhere:"
    echo "----------------------------------------------------------------"
    "$ENGINE_BINARY" models 2>/dev/null | grep -i 'free' || \
      echo "  (none found)"

    echo
    echo "Top 30 model IDs (use this to spot the fork's namespace pattern):"
    echo "----------------------------------------------------------------"
    "$ENGINE_BINARY" models 2>/dev/null | head -30
    ;;

  claude)
    echo
    echo "Claude Code has no free tier. The cheapest model is:"
    echo "  claude-haiku-4-5    (~\$1 per million input, ~\$5 per million output)"
    echo
    echo "If you're on a Pro/Max subscription (no ANTHROPIC_API_KEY set),"
    echo "all usage counts against your monthly quota — haiku is the"
    echo "lowest-quota option."
    echo
    echo "Configured Claude models:"
    echo "  $ENGINE_KNOWN_MODELS"
    ;;

  *)
    echo "Unknown engine: $ENGINE. Add a case branch for it in this script."
    exit 1
    ;;
esac

echo
echo "================================================================"
echo " Next step:"
echo " Edit config/engines/${ENGINE}-free.env and replace the *_MODEL"
echo " lines with IDs from the list above. Then restart the session."
echo "================================================================"
