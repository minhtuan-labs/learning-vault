#!/usr/bin/env bash
set -euo pipefail

# v10.5 — "Where did we leave off?" scan.
#
# Use this when resuming a project the next day, or any time the
# Orchestrator suspects memory/ has drifted from the actual file
# system. It prints a single consolidated snapshot of:
#   - last known project state (memory/_PROJECT_STATE.md)
#   - recent entries from each role's memory file
#   - which docs/ files have real content
#   - whether backend/ and frontend/ have source code
#   - last deployed URL (if any)
#   - open clarifications / pending notifications
#
# Output is plain text designed to be readable by both humans and
# the Orchestrator LLM. Orchestrator should run this on session
# resume and present a brief recap to the user.

echo "================================================================"
echo " Project resume scan ($(date '+%Y-%m-%d %H:%M:%S'))"
echo "================================================================"

echo
echo "## Last known project state (memory/_PROJECT_STATE.md)"
echo "----------------------------------------------------------------"
if [[ -s memory/_PROJECT_STATE.md ]]; then
  cat memory/_PROJECT_STATE.md
else
  echo "  (no project state recorded — treat as fresh project)"
fi

echo
echo "## Role memory — last 30 lines per role"
echo "----------------------------------------------------------------"
for role in ORCHESTRATOR PM SA BA UX BE FE QA DELIVERY; do
  f="memory/${role}.md"
  if [[ -s "$f" ]]; then
    line_count="$(wc -l < "$f" | tr -d ' ')"
    echo
    echo "### ${role}   (${line_count} lines total in $f)"
    tail -n 30 "$f" | sed 's/^/   /'
  fi
done

echo
echo "## Doc files with substantive content (> 200 bytes)"
echo "----------------------------------------------------------------"
found_doc=false
while IFS= read -r f; do
  size=$(wc -c < "$f" 2>/dev/null | tr -d ' ')
  if [[ -n "$size" ]] && (( size > 200 )); then
    printf "  %6s B  %s\n" "$size" "$f"
    found_doc=true
  fi
done < <(find docs planning reports 2>/dev/null -type f -name '*.md' | sort)
if ! $found_doc; then
  echo "  (no substantive docs yet)"
fi

echo
echo "## Source code presence"
echo "----------------------------------------------------------------"
for d in backend frontend; do
  if [[ -d "$d" ]]; then
    count=$(find "$d" -type f \( \
      -name '*.py' -o -name '*.ts' -o -name '*.tsx' -o -name '*.js' \
      -o -name '*.jsx' -o -name '*.go' -o -name '*.rs' -o -name '*.java' \
      \) 2>/dev/null | wc -l | tr -d ' ')
    echo "  $d/  : $count source file(s)"
  else
    echo "  $d/  : directory missing"
  fi
done

echo
echo "## Docker / deployment"
echo "----------------------------------------------------------------"
for f in docker-compose.yml backend/Dockerfile frontend/Dockerfile .env.example; do
  if [[ -f "$f" ]]; then
    echo "  present : $f"
  else
    echo "  missing : $f"
  fi
done

echo
echo "## Last live deployment (docs/delivery/RUNNING_APP.md)"
echo "----------------------------------------------------------------"
if [[ -s docs/delivery/RUNNING_APP.md ]]; then
  head -n 20 docs/delivery/RUNNING_APP.md | sed 's/^/  /'
else
  echo "  (no deployment recorded)"
fi

echo
echo "## QA verdict (reports/TEST_REPORT.md)"
echo "----------------------------------------------------------------"
if [[ -s reports/TEST_REPORT.md ]]; then
  head -n 5 reports/TEST_REPORT.md | sed 's/^/  /'
else
  echo "  (no test report yet)"
fi

echo
echo "## Orchestrator inbox (questions + notifications)"
echo "----------------------------------------------------------------"
if [[ -x scripts/list_pending_questions.sh ]]; then
  bash scripts/list_pending_questions.sh 2>/dev/null | sed 's/^/  /' | head -n 60
else
  echo "  (list_pending_questions.sh missing)"
fi

echo
echo "================================================================"
echo " End of resume scan. Recommended next action for the Orchestrator:"
echo " summarize the above for the user in 3-5 short bullets, then ask"
echo " what to do next (continue current phase, advance phase, etc.)."
echo "================================================================"
