#!/usr/bin/env bash
set -euo pipefail

# v10.12 — Engine-aware model validation.
#
# Usage:
#   bash scripts/check_models.sh                # uses .agent_session ENGINE, or default opencode
#   bash scripts/check_models.sh opencode
#   bash scripts/check_models.sh claude
#
# Exit:
#   0 — all configured models for this engine are reachable
#   1 — engine binary missing
#   2 — at least one model invalid for this engine

ENGINE_ARG="${1:-}"
ENGINE="${ENGINE_ARG:-opencode}"

# If no arg and a session is active, read engine from .agent_session
if [[ -z "$ENGINE_ARG" && -f ".agent_session" ]]; then
  # shellcheck disable=SC1090
  source .agent_session
fi

ENGINE_CFG="config/engines/${ENGINE}.env"
if [[ ! -f "$ENGINE_CFG" ]]; then
  echo "Missing engine config: $ENGINE_CFG"
  echo "Available engines:"
  ls -1 config/engines/*.env 2>/dev/null | sed 's|config/engines/||;s|.env$||' | sed 's/^/  - /'
  exit 1
fi
# shellcheck disable=SC1090
source "$ENGINE_CFG"

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
