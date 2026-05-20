#!/usr/bin/env bash
set -uo pipefail

# v10.20 — Port conflict scanner for DELIVERY.
#
# Two modes:
#
#   1. Check specific ports:
#      bash scripts/check_port_conflicts.sh 8000 8080 5432
#
#   2. Suggest available ports starting from a base:
#      bash scripts/check_port_conflicts.sh --suggest <count> [--from <base>]
#      Example:
#        bash scripts/check_port_conflicts.sh --suggest 3 --from 8000
#        → returns 3 free ports >= 8000 (skipping taken ones)
#
# Output format (machine-readable on stdout, human notes on stderr):
#   PORT=8000 STATUS=FREE
#   PORT=5432 STATUS=TAKEN BY="docker:postgres-other (pid 12345)"
#   PORT=8080 STATUS=TAKEN BY="node (pid 67890)"
#
# DELIVERY uses this to:
#   (a) Show user which of its suggested defaults are conflicting
#   (b) Pick alternates automatically when user picks "auto" mode

MODE="check"
SUGGEST_COUNT=0
SUGGEST_BASE=8000
PORTS_TO_CHECK=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --suggest)
      MODE="suggest"
      SUGGEST_COUNT="${2:-3}"
      shift 2 ;;
    --from)
      SUGGEST_BASE="${2:-8000}"
      shift 2 ;;
    --help|-h)
      sed -n '5,25p' "$0"
      exit 0 ;;
    *)
      PORTS_TO_CHECK+=("$1")
      shift ;;
  esac
done

# Find what's listening on a port. Returns describing string or empty.
#   Strategy: lsof first (works on macOS + Linux), netstat as fallback,
#   docker ps as third look (covers containers that may not appear via
#   lsof on macOS due to vmnetd).
who_owns_port() {
  local port="$1"
  local who=""

  if command -v lsof >/dev/null 2>&1; then
    who=$(lsof -nP -iTCP:"$port" -sTCP:LISTEN 2>/dev/null \
            | awk 'NR==2 {printf "%s (pid %s)", $1, $2}' || true)
  fi

  if [[ -z "$who" ]] && command -v netstat >/dev/null 2>&1; then
    if netstat -an 2>/dev/null | grep -qE "[\.:]${port}[[:space:]]+.*LISTEN"; then
      who="unknown listener"
    fi
  fi

  if [[ -z "$who" ]] && command -v docker >/dev/null 2>&1; then
    local dk
    dk=$(docker ps --format '{{.Names}} {{.Ports}}' 2>/dev/null \
          | grep -E "0\.0\.0\.0:${port}->|:::${port}->" \
          | awk '{print "docker:" $1}' | head -1 || true)
    if [[ -n "$dk" ]]; then who="$dk"; fi
  fi

  echo "$who"
}

is_taken() {
  local port="$1"
  [[ -n "$(who_owns_port "$port")" ]]
}

if [[ "$MODE" == "suggest" ]]; then
  if (( SUGGEST_COUNT < 1 )); then
    echo "ERROR: --suggest count must be >= 1" >&2
    exit 2
  fi
  found=0
  port=$SUGGEST_BASE
  echo "# Suggesting $SUGGEST_COUNT free port(s) starting from $SUGGEST_BASE" >&2
  while (( found < SUGGEST_COUNT )); do
    if (( port > 65535 )); then
      echo "ERROR: ran out of port range before finding $SUGGEST_COUNT free ports" >&2
      exit 1
    fi
    owner=$(who_owns_port "$port")
    if [[ -z "$owner" ]]; then
      echo "PORT=$port STATUS=FREE"
      found=$((found + 1))
    fi
    port=$((port + 1))
  done
  exit 0
fi

# check mode
if [[ ${#PORTS_TO_CHECK[@]} -eq 0 ]]; then
  echo "Usage: bash scripts/check_port_conflicts.sh <port> [<port>...]" >&2
  echo "   or: bash scripts/check_port_conflicts.sh --suggest <N> [--from <base>]" >&2
  exit 2
fi

ANY_TAKEN=0
for port in "${PORTS_TO_CHECK[@]}"; do
  if ! [[ "$port" =~ ^[0-9]+$ ]]; then
    echo "PORT=$port STATUS=INVALID"
    continue
  fi
  owner=$(who_owns_port "$port")
  if [[ -n "$owner" ]]; then
    printf 'PORT=%s STATUS=TAKEN BY="%s"\n' "$port" "$owner"
    ANY_TAKEN=1
  else
    echo "PORT=$port STATUS=FREE"
  fi
done

exit $ANY_TAKEN   # 0 if all free, 1 if any taken
