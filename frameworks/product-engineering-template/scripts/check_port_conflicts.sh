#!/usr/bin/env bash
set -uo pipefail

# v10.22 — Comprehensive port conflict scanner for Deli.
#
# Modes:
#
#   1. Check specific ports (host + docker):
#      bash scripts/check_port_conflicts.sh 8000 8080 5432
#
#   2. Exhaustive scan (host + running docker + stopped docker + nearby compose files):
#      bash scripts/check_port_conflicts.sh --exhaustive 8000 8080 5432
#
#   3. Suggest free ports from a base (skips anything taken):
#      bash scripts/check_port_conflicts.sh --suggest 3 --from 8000
#
#   4. Post-deploy verification (after `docker compose up`):
#      bash scripts/check_port_conflicts.sh --verify 8000 8080 5432
#      Confirms each port is ACTUALLY bound and responding (not just
#      "free" in the host port table — verifies the container is up).
#
# Output (machine-readable on stdout, prose on stderr):
#   PORT=8000 STATUS=FREE
#   PORT=5432 STATUS=TAKEN BY="docker:postgres-other (pid 12345)"
#   PORT=8080 STATUS=TAKEN BY="node (pid 67890)"
#   PORT=3000 STATUS=COMPOSE_CLAIM BY="~/other-project/docker-compose.yml (FE_PORT)"
#   PORT=8000 STATUS=VERIFIED BOUND_BY="nestfi-backend"   (--verify mode)
#   PORT=8000 STATUS=VERIFY_FAIL EXPECTED="bound" GOT="no listener"
#
# Exit codes:
#   0  all ports FREE / VERIFIED
#   1  at least one TAKEN / VERIFY_FAIL / COMPOSE_CLAIM warning

MODE="check"
EXHAUSTIVE=false
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
    --exhaustive)
      EXHAUSTIVE=true
      shift ;;
    --verify)
      MODE="verify"
      shift ;;
    --help|-h)
      sed -n '5,30p' "$0"
      exit 0 ;;
    *)
      PORTS_TO_CHECK+=("$1")
      shift ;;
  esac
done

# ------------------------------------------------------------------
# Find what's listening on a port (host process or running container).
# ------------------------------------------------------------------
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

# ------------------------------------------------------------------
# v10.22 — Find stopped containers that have <port> in their port mapping.
# Stopped containers don't reserve the port, but if Deli or the user
# brings them up later, conflict can happen. Useful heads-up.
# ------------------------------------------------------------------
who_stopped_claims_port() {
  local port="$1"
  command -v docker >/dev/null 2>&1 || { echo ""; return; }
  local dk
  dk=$(docker ps -a --filter status=exited --format '{{.Names}}|{{.Ports}}|{{.Status}}' 2>/dev/null \
        | grep -E ":${port}->" | head -1 | awk -F'|' '{printf "docker-stopped:%s (%s)", $1, $3}' || true)
  echo "$dk"
}

# ------------------------------------------------------------------
# v10.22 — Look for OTHER docker-compose.yml files on the host that
# mention this port (in :PORT mapping form). User may have several
# compose stacks; if two claim 5432, the second `up` will fail.
# ------------------------------------------------------------------
who_compose_claims_port() {
  local port="$1"
  command -v find >/dev/null 2>&1 || { echo ""; return; }
  # Search the user's home (common location) but cap depth to avoid huge scans.
  # Exclude node_modules, .git, .venv to keep it fast.
  local cur_compose
  cur_compose="$(pwd)/docker-compose.yml"
  local hits
  hits=$(find "$HOME" -maxdepth 5 -type f -name 'docker-compose*.yml' 2>/dev/null \
          -not -path '*/node_modules/*' \
          -not -path '*/.git/*' \
          -not -path '*/.venv/*' \
          -not -path '*/venv/*' \
        | xargs -I{} grep -l -E "^[[:space:]]*-?[[:space:]]*\"?${port}:" {} 2>/dev/null \
        | grep -v "^${cur_compose}$" \
        | head -1)
  if [[ -n "$hits" ]]; then
    echo "compose-file:$(echo "$hits" | sed "s|$HOME|~|")"
  else
    echo ""
  fi
}

# ------------------------------------------------------------------
# v10.22 — Post-deploy verify: is the port ACTUALLY bound by something
# responding (not just present in the port table)? Uses nc -z or /dev/tcp.
# Returns the container name that owns it.
# ------------------------------------------------------------------
verify_bound() {
  local port="$1"
  local owner=""
  # Test reachability
  local reachable=false
  if command -v nc >/dev/null 2>&1; then
    if nc -z -w 2 localhost "$port" 2>/dev/null; then reachable=true; fi
  fi
  if ! $reachable; then
    # /dev/tcp fallback (bash builtin)
    if (exec 3<>/dev/tcp/localhost/"$port") 2>/dev/null; then
      reachable=true
      exec 3<&- 2>/dev/null
      exec 3>&- 2>/dev/null
    fi
  fi
  if ! $reachable; then
    echo "VERIFY_FAIL|no listener"
    return 1
  fi
  # Try to identify owner via docker ps
  if command -v docker >/dev/null 2>&1; then
    owner=$(docker ps --format '{{.Names}} {{.Ports}}' 2>/dev/null \
              | grep -E "0\.0\.0\.0:${port}->|:::${port}->" \
              | awk '{print $1}' | head -1 || true)
  fi
  if [[ -z "$owner" ]]; then
    owner="host process"
  fi
  echo "VERIFIED|${owner}"
  return 0
}

is_taken() {
  local port="$1"
  [[ -n "$(who_owns_port "$port")" ]]
}

# ------------------------------------------------------------------
# Suggest mode
# ------------------------------------------------------------------
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
    stopped=$(who_stopped_claims_port "$port")
    compose=$(who_compose_claims_port "$port")
    if [[ -z "$owner" ]]; then
      if [[ -n "$stopped" ]] || [[ -n "$compose" ]]; then
        # FREE now but conflict potential — note it
        local_note=""
        [[ -n "$stopped" ]] && local_note="$local_note stopped=$stopped"
        [[ -n "$compose" ]] && local_note="$local_note compose=$compose"
        echo "PORT=$port STATUS=FREE NOTE=\"potential reuse:$local_note\""
      else
        echo "PORT=$port STATUS=FREE"
      fi
      found=$((found + 1))
    fi
    port=$((port + 1))
  done
  exit 0
fi

# ------------------------------------------------------------------
# Verify mode (post-deploy)
# ------------------------------------------------------------------
if [[ "$MODE" == "verify" ]]; then
  if [[ ${#PORTS_TO_CHECK[@]} -eq 0 ]]; then
    echo "Usage: bash scripts/check_port_conflicts.sh --verify <port> [<port>...]" >&2
    exit 2
  fi
  echo "# Post-deploy verification — checking each port is actually bound and responding" >&2
  ANY_FAIL=0
  for port in "${PORTS_TO_CHECK[@]}"; do
    if ! [[ "$port" =~ ^[0-9]+$ ]]; then
      echo "PORT=$port STATUS=INVALID"
      continue
    fi
    result=$(verify_bound "$port")
    IFS='|' read -r status detail <<< "$result"
    if [[ "$status" == "VERIFIED" ]]; then
      echo "PORT=$port STATUS=VERIFIED BOUND_BY=\"$detail\""
    else
      echo "PORT=$port STATUS=VERIFY_FAIL EXPECTED=\"bound\" GOT=\"$detail\""
      ANY_FAIL=1
    fi
  done
  exit $ANY_FAIL
fi

# ------------------------------------------------------------------
# Check mode (default)
# ------------------------------------------------------------------
if [[ ${#PORTS_TO_CHECK[@]} -eq 0 ]]; then
  echo "Usage: bash scripts/check_port_conflicts.sh <port> [<port>...]" >&2
  echo "   or: bash scripts/check_port_conflicts.sh --exhaustive <port> [<port>...]" >&2
  echo "   or: bash scripts/check_port_conflicts.sh --suggest <N> [--from <base>]" >&2
  echo "   or: bash scripts/check_port_conflicts.sh --verify <port> [<port>...]" >&2
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
    continue
  fi
  # Port currently FREE — in exhaustive mode also check stopped containers + compose files
  if $EXHAUSTIVE; then
    stopped=$(who_stopped_claims_port "$port")
    if [[ -n "$stopped" ]]; then
      printf 'PORT=%s STATUS=STOPPED_CLAIM BY="%s"\n' "$port" "$stopped"
      ANY_TAKEN=1
      continue
    fi
    compose=$(who_compose_claims_port "$port")
    if [[ -n "$compose" ]]; then
      printf 'PORT=%s STATUS=COMPOSE_CLAIM BY="%s"\n' "$port" "$compose"
      ANY_TAKEN=1
      continue
    fi
  fi
  echo "PORT=$port STATUS=FREE"
done

exit $ANY_TAKEN
