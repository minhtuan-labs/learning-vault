#!/usr/bin/env bash
set -euo pipefail

# v10.8 — Verify a role has the upstream inputs it needs before starting.
#
# Usage:
#   bash scripts/check_prerequisites.sh <ROLE>
#
# Exit codes:
#   0  — all required inputs are present with substantive content
#   1  — one or more inputs are missing or are skeleton-only
#   2  — usage error / unknown role
#
# Output: a structured report listing each required file, its current
# status, and (when something is missing) the role that owns producing
# it. Workers and the Orchestrator both call this — workers to decide
# whether to proceed; Orchestrator to know which upstream roles to
# coordinate.

ROLE="${1:-}"
if [[ -z "$ROLE" ]]; then
  echo "Usage: bash scripts/check_prerequisites.sh <ROLE>"
  echo "Roles: PM SA BA UX BE FE QA DELIVERY ORCHESTRATOR"
  exit 2
fi

# Substantive content threshold in bytes. Files smaller than this are
# treated as "skeleton" (i.e. the role-skeleton headings only) and do
# NOT satisfy a prerequisite.
THRESHOLD="${PREREQ_THRESHOLD:-200}"

# get_prereqs <ROLE> → space-separated list of required input files.
# Output the files in priority order so the report reads naturally.
get_prereqs() {
  case "$1" in
    PM)
      # PM only needs the product idea to start. Later refinement
      # tasks may need more, but the role itself depends only on this.
      echo "PRODUCT_IDEA.md"
      ;;
    BA)
      # BA needs the idea; PRD is optional but recommended.
      echo "PRODUCT_IDEA.md"
      ;;
    UX)
      # UX needs the idea + the PRD to draw flows against.
      echo "PRODUCT_IDEA.md docs/product/PRD.md"
      ;;
    SA)
      # SA depends on PM + BA upstream outputs.
      echo "PRODUCT_IDEA.md docs/product/PRD.md docs/business/USER_STORIES.md docs/business/BUSINESS_REQUIREMENTS.md"
      ;;
    BE)
      # BE depends on SA's architecture + tech stack + API contract,
      # and the user stories that drive backend behaviour.
      echo "docs/architecture/SOLUTION_ARCHITECTURE.md docs/architecture/TECH_STACK.md docs/architecture/API_CONTRACT.md docs/business/USER_STORIES.md"
      ;;
    FE)
      # FE depends on UX flow + API contract + tech stack.
      echo "docs/product/UX_FLOW.md docs/architecture/API_CONTRACT.md docs/architecture/TECH_STACK.md"
      ;;
    QA)
      # QA needs stories to validate, API contract to script against,
      # and an agreed backlog of acceptance criteria.
      echo "docs/business/USER_STORIES.md docs/architecture/API_CONTRACT.md planning/BACKLOG.md"
      ;;
    DELIVERY)
      # DELIVERY refuses to ship unless QA produced a PASS verdict,
      # SA pinned the stack with user confirmation, BE/FE actually
      # wrote code, and no critical/major bugs remain open.
      echo "reports/TEST_REPORT.md docs/architecture/TECH_STACK.md _SIGNED_TECH_STACK_ _VERDICT_PASS_ _NO_OPEN_CRITICAL_MAJOR_ _CODE_BE_ _CODE_FE_"
      ;;
    ORCHESTRATOR)
      # Orchestrator only needs the product idea to start coordinating.
      echo "PRODUCT_IDEA.md"
      ;;
    *)
      echo ""
      ;;
  esac
}

# get_owner <file> → role responsible for producing it. USER means the
# human owner — workers must use ask_orchestrator.sh, not
# notify_orchestrator.sh, when a USER-owned file is missing.
get_owner() {
  case "$1" in
    PRODUCT_IDEA.md)                            echo "USER" ;;
    docs/product/PRD.md)                        echo "PM" ;;
    docs/product/ROADMAP.md)                    echo "PM" ;;
    docs/product/UX_FLOW.md)                    echo "UX" ;;
    docs/product/WIREFRAMES.md)                 echo "UX" ;;
    docs/product/DESIGN_NOTES.md)               echo "UX" ;;
    docs/business/BUSINESS_REQUIREMENTS.md)     echo "BA" ;;
    docs/business/USER_STORIES.md)              echo "BA" ;;
    docs/business/DOMAIN_MODEL.md)              echo "BA" ;;
    docs/architecture/SOLUTION_ARCHITECTURE.md) echo "SA" ;;
    docs/architecture/TECH_STACK.md)            echo "SA" ;;
    docs/architecture/ADR.md)                   echo "SA" ;;
    docs/architecture/API_CONTRACT.md)          echo "SA" ;;
    planning/BACKLOG.md)                        echo "PM" ;;
    planning/BE_PLAN.md)                        echo "BE" ;;
    planning/FE_PLAN.md)                        echo "FE" ;;
    docs/qa/TEST_PLAN.md)                       echo "QA" ;;
    docs/qa/TEST_CASES.md)                      echo "QA" ;;
    reports/TEST_REPORT.md)                     echo "QA" ;;
    reports/BUG_REPORT.md)                      echo "QA" ;;
    docs/delivery/DELIVERY_PLAN.md)             echo "DELIVERY" ;;
    docs/delivery/RUNNING_APP.md)               echo "DELIVERY" ;;
    *)                                           echo "?" ;;
  esac
}

# Special semantic check: for DELIVERY, reports/TEST_REPORT.md must
# additionally start with VERDICT: PASS to be considered "satisfied".
verdict_is_pass() {
  local file="$1"
  [[ -f "$file" ]] || return 1
  local first_line
  first_line="$(grep -m1 -E '^[A-Za-z]' "$file" 2>/dev/null || true)"
  [[ "$first_line" =~ ^VERDICT:\ PASS ]]
}

# Synthetic token check used by check_phase_gate.sh as well. Returns
# 0 / 1 and echoes a status line.
check_synthetic_token() {
  local token="$1"
  case "$token" in
    _CODE_BE_)
      local count
      count=$(find backend -type f \( -name '*.py' -o -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx' -o -name '*.go' -o -name '*.rs' -o -name '*.java' -o -name '*.rb' \) 2>/dev/null | wc -l | tr -d ' ')
      if [[ -n "$count" ]] && (( count > 0 )); then
        echo "OK (${count} source files in backend/)"
        return 0
      fi
      echo "MISSING (no source files in backend/ — BE has not built yet)"
      return 1
      ;;
    _CODE_FE_)
      local count
      count=$(find frontend -type f \( -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx' -o -name '*.vue' -o -name '*.svelte' -o -name '*.astro' -o -name '*.html' \) 2>/dev/null | wc -l | tr -d ' ')
      if [[ -n "$count" ]] && (( count > 0 )); then
        echo "OK (${count} source files in frontend/)"
        return 0
      fi
      echo "MISSING (no source files in frontend/ — FE has not built yet)"
      return 1
      ;;
    _SIGNED_TECH_STACK_)
      if [[ -f docs/architecture/TECH_STACK.md ]] && grep -qi "Confirmed by user" docs/architecture/TECH_STACK.md; then
        echo "OK (TECH_STACK.md confirmed by user)"
        return 0
      fi
      echo "MISSING (TECH_STACK.md lacks 'Confirmed by user' line — SA skipped Tech Stack Confirmation Protocol)"
      return 1
      ;;
    _VERDICT_PASS_)
      if verdict_is_pass reports/TEST_REPORT.md; then
        echo "OK (VERDICT: PASS)"
        return 0
      fi
      local first
      first=$(grep -m1 -E '^[A-Za-z]' reports/TEST_REPORT.md 2>/dev/null || echo '(empty)')
      echo "MISSING (TEST_REPORT.md verdict: ${first})"
      return 1
      ;;
    _NO_OPEN_CRITICAL_MAJOR_)
      if [[ ! -f reports/BUG_REPORT.md ]]; then
        echo "OK (no BUG_REPORT.md — assume clean)"
        return 0
      fi
      local hits
      hits=$(grep -ciE '^[-*[:space:]]*Status:[[:space:]]*(OPEN_CRITICAL|OPEN_MAJOR|RETEST_FAIL)' reports/BUG_REPORT.md 2>/dev/null || echo 0)
      if [[ -n "$hits" ]] && (( hits > 0 )); then
        echo "MISSING (${hits} bug(s) with OPEN_CRITICAL / OPEN_MAJOR / RETEST_FAIL in BUG_REPORT.md — release blocked)"
        return 1
      fi
      echo "OK (no critical/major bugs open)"
      return 0
      ;;
    *)
      echo "UNKNOWN_TOKEN"
      return 1
      ;;
  esac
}

prereqs="$(get_prereqs "$ROLE")"
if [[ -z "$prereqs" ]]; then
  echo "Unknown role: $ROLE"
  echo "Roles: PM SA BA UX BE FE QA DELIVERY ORCHESTRATOR"
  exit 2
fi

echo "================================================================"
echo " Prerequisite check for $ROLE"
echo " (substantive content threshold: ${THRESHOLD} bytes)"
echo "================================================================"

missing_files=()
missing_owners=()
user_owned_missing=false

for f in $prereqs; do
  status=""

  # Synthetic tokens (start with _ and end with _) are handled separately.
  if [[ "$f" == _*_ ]]; then
    if status="$(check_synthetic_token "$f")"; then
      printf "  %-50s  owner=%-10s  %s\n" "$f" "(semantic)" "$status"
    else
      printf "  %-50s  owner=%-10s  %s\n" "$f" "(semantic)" "$status"
      missing_files+=("$f")
      # Synthetic tokens map to owners — _CODE_BE_/_VERDICT_PASS_ etc.
      case "$f" in
        _CODE_BE_) missing_owners+=("BE") ;;
        _CODE_FE_) missing_owners+=("FE") ;;
        _SIGNED_TECH_STACK_) missing_owners+=("SA") ;;
        _VERDICT_PASS_) missing_owners+=("QA") ;;
        _NO_OPEN_CRITICAL_MAJOR_) missing_owners+=("BE,FE,QA") ;;
        *) missing_owners+=("?") ;;
      esac
    fi
    continue
  fi

  owner="$(get_owner "$f")"

  if [[ ! -f "$f" ]]; then
    status="MISSING"
  else
    sz=$(wc -c < "$f" 2>/dev/null | tr -d ' ')
    if [[ -z "$sz" ]] || (( sz < THRESHOLD )); then
      status="SKELETON (${sz}B < ${THRESHOLD}B)"
    elif [[ "$ROLE" == "DELIVERY" && "$f" == "reports/TEST_REPORT.md" ]]; then
      if verdict_is_pass "$f"; then
        status="OK (VERDICT: PASS)"
      else
        first_line="$(grep -m1 -E '^[A-Za-z]' "$f" 2>/dev/null || echo '(no verdict line)')"
        status="NOT_PASS — first non-blank line: ${first_line}"
      fi
    else
      status="OK (${sz}B)"
    fi
  fi

  printf "  %-50s  owner=%-10s  %s\n" "$f" "$owner" "$status"

  case "$status" in
    OK*) ;;
    *)
      missing_files+=("$f")
      missing_owners+=("$owner")
      if [[ "$owner" == "USER" ]]; then
        user_owned_missing=true
      fi
      ;;
  esac
done

echo

if [[ ${#missing_files[@]} -eq 0 ]]; then
  echo "OK — $ROLE has every required input. Proceed with the task."
  exit 0
fi

# Build a comma-separated missing list and unique owners list for the
# guidance text.
missing_csv="$(IFS=, ; echo "${missing_files[*]}")"
# unique owners (preserve order)
unique_owners=()
for o in "${missing_owners[@]}"; do
  found=false
  for u in "${unique_owners[@]:-}"; do
    if [[ "$u" == "$o" ]]; then found=true; break; fi
  done
  $found || unique_owners+=("$o")
done
owners_csv="$(IFS=, ; echo "${unique_owners[*]}")"

echo "BLOCKED — $ROLE cannot proceed. ${#missing_files[@]} missing input(s)."
echo
echo "Required action for $ROLE (DO NOT fake the missing inputs):"
echo
if $user_owned_missing; then
  echo "  Some missing files are owned by USER (e.g. PRODUCT_IDEA.md)."
  echo "  Use ask_orchestrator.sh so the user can fill them in:"
  echo
  echo "    bash scripts/ask_orchestrator.sh $ROLE \"Cannot proceed — missing user-owned inputs: ${missing_csv}. Please fill PRODUCT_IDEA.md (or the relevant file) before I continue.\""
fi
if [[ "$owners_csv" != "USER" && -n "$owners_csv" ]]; then
  echo
  echo "  Some missing files are owned by other agents (${owners_csv})."
  echo "  Do BOTH of the following before you exit (v10.14):"
  echo
  echo "  (a) Notify the Orchestrator so the user can see you are parked:"
  echo
  echo "    bash scripts/notify_orchestrator.sh $ROLE \"Cannot proceed — missing inputs: ${missing_csv}. Need ${owners_csv}. Parking via file_watch for auto-resume.\""
  echo
  echo "  (b) Register a file watch for EACH agent-owned missing file so"
  echo "      the watcher_daemon auto-reroutes you when the upstream"
  echo "      owner produces it — no user action required:"
  echo
  for i in "${!missing_files[@]}"; do
    f="${missing_files[$i]}"
    o="${missing_owners[$i]}"
    [[ "$o" == "USER" ]] && continue
    # Skip synthetic tokens (start/end with _)
    [[ "$f" == _*_ ]] && continue
    echo "    bash scripts/file_watch.sh $ROLE $f \"Resume: $f is now available. Re-read upstream inputs and continue your original task.\""
  done
fi
echo
echo "Then append a 'blocked on missing inputs' entry to memory/$ROLE.md"
echo "and EXIT this turn. Do NOT proceed with placeholder / best-guess"
echo "content for files another role owns. The watcher_daemon will"
echo "auto-reroute you when the upstream file lands."
echo "================================================================"
exit 1
