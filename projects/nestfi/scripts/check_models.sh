#!/usr/bin/env bash
set -euo pipefail

# v10.12 / v10.16.2 — Engine-aware model validation.
#
# Usage:
#   bash scripts/check_models.sh                  # uses .agent_session ENGINE
#   bash scripts/check_models.sh opencode         # base engine only
#   bash scripts/check_models.sh claude
#   bash scripts/check_models.sh opencode --free  # base + free overlay
#   bash scripts/check_models.sh opencode-free    # shorthand for the above
#
# Exit:
#   0 — all configured models for this engine are reachable
#   1 — engine binary missing
#   2 — at least one model invalid for this engine

# ---- parse args ----
ENGINE_ARG="${1:-}"
FREE_FLAG=false
if [[ "${2:-}" == "--free" ]]; then
  FREE_FLAG=true
fi

# Shorthand: `check_models.sh opencode-free` → engine=opencode + free overlay.
# This was the form that broke in v10.16 because we treated opencode-free
# as an engine name.
if [[ "$ENGINE_ARG" == *-free ]]; then
  ENGINE_ARG="${ENGINE_ARG%-free}"
  FREE_FLAG=true
fi

ENGINE="${ENGINE_ARG:-opencode}"

# If no engine arg and a session is active, inherit ENGINE and FREE_MODE
# from .agent_session — that's what the running session is actually using.
if [[ -z "$ENGINE_ARG" && -f ".agent_session" ]]; then
  # shellcheck disable=SC1090
  source .agent_session
  if [[ "${FREE_MODE:-false}" == "true" ]]; then
    FREE_FLAG=true
  fi
fi

ENGINE_CFG="config/engines/${ENGINE}.env"
if [[ ! -f "$ENGINE_CFG" ]]; then
  echo "Missing engine config: $ENGINE_CFG"
  echo "Available engines:"
  ls -1 config/engines/*.env 2>/dev/null | grep -v '\-free\.env$' \
    | sed 's|config/engines/||;s|.env$||' | sed 's/^/  - /'
  echo
  echo "Note: <engine>-free.env files are overlays, not standalone engines."
  echo "      Pass them via --free or the <engine>-free shorthand."
  exit 1
fi
# shellcheck disable=SC1090
source "$ENGINE_CFG"

# v10.16.2 — apply --free overlay AFTER base config so ENGINE_BINARY is
# defined before the overlay (which only sets *_MODEL) runs.
if [[ "$FREE_FLAG" == "true" ]]; then
  FREE_CFG="config/engines/${ENGINE}-free.env"
  if [[ -f "$FREE_CFG" ]]; then
    # shellcheck disable=SC1090
    source "$FREE_CFG"
    echo "(--free overlay active — sourced $FREE_CFG)"
  else
    echo "WARN: --free requested but $FREE_CFG not found. Using paid defaults."
  fi
fi

echo "================================================================"
echo " Model validation — engine=$ENGINE  binary=$ENGINE_BINARY"
echo " Mode: $ENGINE_MODEL_CHECK_MODE"
echo "================================================================"

if ! command -v "$ENGINE_BINARY" >/dev/null 2>&1; then
  echo "ERROR: engine binary '$ENGINE_BINARY' not found in PATH."
  exit 1
fi

echo "$ENGINE_BINARY version:"
"$ENGINE_BINARY" --version 2>&1 | head -3 || true
echo

echo "Configured models for $ENGINE:"
for agent in ORCHESTRATOR PM SA BA UX BE FE QA DELIVERY; do
  var_name="${agent}_MODEL"
  echo "  $agent=${!var_name:-not_configured}"
done
echo

FAILED=0

if [[ "$ENGINE_MODEL_CHECK_MODE" == "dynamic" ]]; then
  echo "Fetching model list: $ENGINE_MODELS_LIST_CMD"
  MODELS_OUTPUT="$($ENGINE_MODELS_LIST_CMD 2>/dev/null || true)"
  if [[ -z "$MODELS_OUTPUT" ]]; then
    echo "WARNING: '$ENGINE_MODELS_LIST_CMD' returned empty output."
    echo "Try running manually: $ENGINE_MODELS_LIST_CMD"
    exit 1
  fi
  echo
  echo "Validation result:"
  for agent in ORCHESTRATOR PM SA BA UX BE FE QA DELIVERY; do
    var_name="${agent}_MODEL"
    model="${!var_name:-}"
    if [[ -z "$model" ]]; then
      echo "  ❌ $agent: not configured"
      FAILED=1; continue
    fi
    if echo "$MODELS_OUTPUT" | grep -Fq "$model"; then
      echo "  ✅ $agent: $model"
    else
      echo "  ❌ $agent: $model NOT FOUND in $ENGINE_MODELS_LIST_CMD"
      FAILED=1
    fi
  done

elif [[ "$ENGINE_MODEL_CHECK_MODE" == "static" ]]; then
  echo "Known models (from ENGINE_KNOWN_MODELS):"
  for m in $ENGINE_KNOWN_MODELS; do echo "  - $m"; done
  echo
  echo "Validation result:"
  for agent in ORCHESTRATOR PM SA BA UX BE FE QA DELIVERY; do
    var_name="${agent}_MODEL"
    model="${!var_name:-}"
    if [[ -z "$model" ]]; then
      echo "  ❌ $agent: not configured"
      FAILED=1; continue
    fi
    found=false
    for known in $ENGINE_KNOWN_MODELS; do
      [[ "$known" == "$model" ]] && { found=true; break; }
    done
    if $found; then
      echo "  ✅ $agent: $model"
    else
      echo "  ❌ $agent: $model NOT IN whitelist"
      FAILED=1
    fi
  done
else
  echo "Unknown ENGINE_MODEL_CHECK_MODE: $ENGINE_MODEL_CHECK_MODE"
  exit 1
fi

echo
if [[ "$FAILED" -ne 0 ]]; then
  echo "Some configured model IDs are invalid."
  echo "Edit: $ENGINE_CFG"
  exit 2
fi
echo "All configured models were validated."
