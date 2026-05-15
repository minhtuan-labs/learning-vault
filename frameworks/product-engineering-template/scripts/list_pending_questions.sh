#!/usr/bin/env bash
set -euo pipefail

# v10.3 — Orchestrator inbox.
#
# Surfaces two things the user should see at the start of a turn:
#   1. Clarification requests filed by workers via ask_orchestrator.sh
#      (require a user answer; resolved by answer_role.sh).
#   2. One-way notifications filed by workers via notify_orchestrator.sh
#      (no answer expected — status events like "tests PASS",
#      "deployed at http://localhost:3000").
#
# The script keeps its old name for backward compatibility, but now
# acts as a unified Orchestrator inbox.

QUESTIONS_DIR=".pane_questions"
ANSWERS_DIR=".pane_answers"
NOTIF_DIR=".pane_notifications"

echo "================================================================"
echo " Orchestrator inbox"
echo "================================================================"

# ---- 1. Pending clarification questions --------------------------------
echo
echo "[1] Clarification requests waiting for the user"
echo "----------------------------------------------------------------"

q_found=0
if [[ -d "$QUESTIONS_DIR" ]]; then
  for q in "$QUESTIONS_DIR"/*.md; do
    [[ -f "$q" ]] || continue
    qid="$(basename "$q" .md)"
    ans="$ANSWERS_DIR/$qid.md"
    if [[ -f "$ans" ]]; then
      continue   # already answered
    fi
    q_found=$((q_found+1))
    echo
    echo " Question id : $qid"
    echo " File        : $q"
    echo " ------------------------------------------------------------"
    sed 's/^/   /' "$q"
  done
fi

if [[ $q_found -eq 0 ]]; then
  echo "  (none)"
else
  echo
  echo " To answer:"
  echo "   bash scripts/answer_role.sh <ROLE> <question_id> \"<answer>\""
fi

# ---- 2. Notifications --------------------------------------------------
echo
echo "----------------------------------------------------------------"
echo "[2] Notifications from workers (one-way, no answer needed)"
echo "----------------------------------------------------------------"

n_found=0
if [[ -d "$NOTIF_DIR" ]]; then
  for n in "$NOTIF_DIR"/*.md; do
    [[ -f "$n" ]] || continue
    nid="$(basename "$n" .md)"
    n_found=$((n_found+1))
    echo
    echo " Notif id    : $nid"
    echo " File        : $n"
    echo " ------------------------------------------------------------"
    sed 's/^/   /' "$n"
  done
fi

if [[ $n_found -eq 0 ]]; then
  echo "  (none)"
else
  echo
  echo " Notifications stay in $NOTIF_DIR/ until you clear them. You can"
  echo " safely 'rm $NOTIF_DIR/*.md' once you've shown them to the user."
fi

echo
echo "================================================================"
TOTAL=$((q_found + n_found))
echo " Inbox summary: ${q_found} question(s), ${n_found} notification(s)."
echo "================================================================"
