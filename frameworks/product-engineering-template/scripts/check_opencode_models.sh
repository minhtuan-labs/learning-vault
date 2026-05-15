#!/usr/bin/env bash
set -euo pipefail

MODEL_CONFIG_FILE="config/agent_models.env"
OPENCODE_CONFIG_FILE="config/opencode.env"

if [[ -f "$MODEL_CONFIG_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$MODEL_CONFIG_FILE"
else
  echo "Missing $MODEL_CONFIG_FILE"
  exit 1
fi

if [[ -f "$OPENCODE_CONFIG_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$OPENCODE_CONFIG_FILE"
fi

OPENCODE_PROVIDER="${OPENCODE_PROVIDER:-opencode-go}"

if ! command -v opencode >/dev/null 2>&1; then
  echo "ERROR: opencode command not found in PATH."
  exit 1
fi

echo "OpenCode version:"
opencode --version || true
echo

echo "Configured agent models:"
for agent in ORCHESTRATOR PM SA BA UX BE FE QA DELIVERY; do
  var_name="${agent}_MODEL"
  echo "  $agent=${!var_name:-not_configured}"
done
echo

echo "Fetching available models..."
MODELS_OUTPUT="$(opencode models 2>/dev/null || true)"

if [[ -z "$MODELS_OUTPUT" ]]; then
  echo "WARNING: 'opencode models' returned empty output."
  echo "Try running manually:"
  echo "  opencode models"
  echo "  opencode models $OPENCODE_PROVIDER"
  exit 1
fi

echo
echo "Validation result:"
FAILED=0

for agent in ORCHESTRATOR PM SA BA UX BE FE QA DELIVERY; do
  var_name="${agent}_MODEL"
  model="${!var_name:-}"
  if [[ -z "$model" || "$model" == "not_configured" ]]; then
    echo "  ❌ $agent: not configured"
    FAILED=1
    continue
  fi

  if echo "$MODELS_OUTPUT" | grep -Fq "$model"; then
    echo "  ✅ $agent: $model"
  else
    echo "  ❌ $agent: $model not found in 'opencode models'"
    FAILED=1
  fi
done

echo
echo "Useful command to inspect exact IDs:"
echo "  opencode models"
echo "  opencode models $OPENCODE_PROVIDER"

if [[ "$FAILED" -ne 0 ]]; then
  echo
  echo "Some configured model IDs were not found."
  echo "Edit config/agent_models.env using the exact IDs returned by OpenCode."
  exit 2
fi

echo
echo "All configured models were found."
