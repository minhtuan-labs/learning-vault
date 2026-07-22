#!/usr/bin/env bash
set -euo pipefail

# v10.24 — Cost report: close the loop on the framework's core value prop
# ("don't pay for one strong model to do nine jobs").
#
# The framework deliberately runs each role on a different-cost model.
# This script measures whether that mix actually saves money by
# estimating token spend per ROLE, per PHASE, and per MODEL from the
# routing receipts + per-run logs that route_to_pane.sh already writes.
#
# DATA SOURCES (all written by the existing framework, nothing new needed):
#   .pane_logs/_routing_receipts.log  — one block per routing: role, model,
#                                       task_file, log_file
#   .pane_tasks/<ROLE>_<TS>.md        — the prompt injected into the worker
#                                       (proxy for INPUT tokens)
#   .pane_logs/<ROLE>_<TS>.log        — captured engine output
#                                       (proxy for OUTPUT tokens)
#   memory/_PROJECT_STATE.md          — "advanced to <phase>" session log
#                                       (used to attribute each run to a phase)
#   config/model_prices.env           — USD per 1M tokens, per model
#
# IMPORTANT — this is an ESTIMATE. Engines run in --print/run mode don't
# emit a usage line we can trust, so token counts are derived from
# character counts (chars / TOKENS_PER_CHAR_DIVISOR). Prices drift. Treat
# the output as a relative cost comparison across roles, not an invoice.
#
# Usage:
#   bash scripts/cost_report.sh                # summary: by phase, by role, total
#   bash scripts/cost_report.sh --by-run       # + one line per routed task
#   bash scripts/cost_report.sh --json         # machine-readable
#
# Exit codes: 0 ok (even with no data), 2 usage error.

MODE="summary"
case "${1:-}" in
  "")           MODE="summary" ;;
  --by-run)     MODE="by-run" ;;
  --json)       MODE="json" ;;
  -h|--help)
    grep -E '^#( |$)' "$0" | sed 's/^# \{0,1\}//'
    exit 0
    ;;
  *)
    echo "Unknown arg: $1" >&2
    echo "Usage: bash scripts/cost_report.sh [--by-run|--json]" >&2
    exit 2
    ;;
esac

RECEIPTS=".pane_logs/_routing_receipts.log"
PRICES_FILE="${MODEL_PRICES_FILE:-config/model_prices.env}"
STATE_FILE="memory/_PROJECT_STATE.md"
# Average characters per token. 4 is a decent English/code approximation.
DIV="${TOKENS_PER_CHAR_DIVISOR:-4}"

if [[ ! -f "$RECEIPTS" ]]; then
  if [[ "$MODE" == "json" ]]; then
    echo '{"runs":[],"note":"no routing receipts yet — has the team run?"}'
  else
    echo "No routing receipts found at $RECEIPTS."
    echo "Either the team hasn't run yet, or you're not in the project root."
  fi
  exit 0
fi

# --- price lookup (avoids bash-4 associative arrays for macOS bash 3.2) ---
price_for() {  # echoes "INPUT_USD_PER_1M OUTPUT_USD_PER_1M"
  local model="$1" line val
  if [[ -f "$PRICES_FILE" ]]; then
    line=$(grep -E "^${model}=" "$PRICES_FILE" 2>/dev/null | tail -1 || true)
    if [[ -z "$line" ]]; then
      line=$(grep -E "^DEFAULT=" "$PRICES_FILE" 2>/dev/null | tail -1 || true)
    fi
    val="${line#*=}"
    if [[ "$val" == *:* ]]; then
      echo "${val%%:*} ${val##*:}"
      return
    fi
  fi
  echo "0 0"
}

# numeric, sortable form of "YYYY-MM-DD HH:MM:SS" -> digits only
ts_num() { echo "${1//[^0-9]/}"; }

# --- build the phase timeline from _PROJECT_STATE.md session log ---
# Lines look like:  - 2026-05-14 16:59:38 — advanced to 0_DISCOVERY
PHASE_TL="$(mktemp)"
trap 'rm -f "$PHASE_TL" "$RUNS_TMP" 2>/dev/null || true' EXIT
if [[ -f "$STATE_FILE" ]]; then
  grep -E 'advanced to ' "$STATE_FILE" 2>/dev/null | while IFS= read -r l; do
    pts=$(echo "$l" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}' | head -1 || true)
    ph=$(echo "$l" | sed -E 's/.*advanced to[[:space:]]*//' | awk '{print $1}')
    [[ -n "$pts" && -n "$ph" ]] && echo "$(ts_num "$pts") $ph"
  done | sort -n > "$PHASE_TL" || true
fi

phase_for() {  # given a run's numeric ts, find latest phase advance <= it
  local rts="$1" ph="(unattributed)" pn pp
  while read -r pn pp; do
    [[ -z "$pn" ]] && continue
    if (( pn <= rts )); then ph="$pp"; else break; fi
  done < "$PHASE_TL"
  echo "$ph"
}

# --- walk receipts, emit one normalized record per run ---
RUNS_TMP="$(mktemp)"
cur_ts=""; cur_role=""; cur_model=""; cur_task=""; cur_log=""

flush_run() {
  [[ -z "$cur_role" ]] && return
  local in_chars=0 out_chars=0 in_tok out_tok prices in_p out_p cost phase rnum
  [[ -f "$cur_task" ]] && in_chars=$(wc -c < "$cur_task" 2>/dev/null | tr -d ' ')
  [[ -f "$cur_log"  ]] && out_chars=$(wc -c < "$cur_log"  2>/dev/null | tr -d ' ')
  in_tok=$(( ${in_chars:-0} / DIV ))
  out_tok=$(( ${out_chars:-0} / DIV ))
  prices="$(price_for "$cur_model")"
  in_p="${prices%% *}"; out_p="${prices##* }"
  cost=$(awk -v it="$in_tok" -v ot="$out_tok" -v ip="$in_p" -v op="$out_p" \
        'BEGIN{ printf "%.6f", it/1000000.0*ip + ot/1000000.0*op }')
  rnum=$(ts_num "$cur_ts")
  phase="$(phase_for "$rnum")"
  # tab-separated: ts role phase model in_tok out_tok cost
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$cur_ts" "$cur_role" "$phase" "$cur_model" "$in_tok" "$out_tok" "$cost" >> "$RUNS_TMP"
}

while IFS= read -r line; do
  if [[ "$line" =~ ^\[(.+)\]\ route_to_pane\.sh\ -\>\ ([A-Z]+)\ \(pane=.*model=(.+)\)$ ]]; then
    flush_run
    cur_ts="${BASH_REMATCH[1]}"
    cur_role="${BASH_REMATCH[2]}"
    cur_model="${BASH_REMATCH[3]}"
    cur_task=""; cur_log=""
  elif [[ "$line" =~ ^[[:space:]]+task_file=(.+)$ ]]; then
    cur_task="${BASH_REMATCH[1]}"
  elif [[ "$line" =~ ^[[:space:]]+log_file=(.+)$ ]]; then
    cur_log="${BASH_REMATCH[1]}"
  fi
done < "$RECEIPTS"
flush_run

RUN_COUNT=$(wc -l < "$RUNS_TMP" | tr -d ' ')

if [[ "$MODE" == "json" ]]; then
  awk -F'\t' '
    BEGIN{ printf "{\"runs\":[" }
    { if(NR>1) printf ",";
      printf "{\"ts\":\"%s\",\"role\":\"%s\",\"phase\":\"%s\",\"model\":\"%s\",\"in_tokens\":%d,\"out_tokens\":%d,\"cost_usd\":%s}",
        $1,$2,$3,$4,$5,$6,$7; t+=$7 }
    END{ printf "],\"total_cost_usd\":%.6f}\n", t }
  ' "$RUNS_TMP"
  exit 0
fi

echo "================================================================"
echo " Cost report  (ESTIMATE — chars/${DIV} tokens, prices=${PRICES_FILE})"
echo " Routed runs: ${RUN_COUNT}"
echo "================================================================"

if (( RUN_COUNT == 0 )); then
  echo "No completed runs parsed from receipts."
  exit 0
fi

echo
echo "By phase:"
awk -F'\t' '{ tok[$3]+=$5+$6; cost[$3]+=$7; n[$3]++ }
  END{ for(p in cost) printf "  %-28s  %4d run(s)  %10d tok  $%9.4f\n", p, n[p], tok[p], cost[p] }' \
  "$RUNS_TMP" | sort

echo
echo "By role (this is the cost-mix you tuned):"
awk -F'\t' '{ tok[$2]+=$5+$6; cost[$2]+=$7; n[$2]++; mdl[$2]=$4 }
  END{ for(r in cost) printf "  %-12s %-26s %4d run(s)  %10d tok  $%9.4f\n", r, mdl[r], n[r], tok[r], cost[r] }' \
  "$RUNS_TMP" | sort -t'$' -k2 -nr

echo
echo "By model:"
awk -F'\t' '{ tok[$4]+=$5+$6; cost[$4]+=$7; n[$4]++ }
  END{ for(m in cost) printf "  %-28s  %4d run(s)  %10d tok  $%9.4f\n", m, n[m], tok[m], cost[m] }' \
  "$RUNS_TMP" | sort

if [[ "$MODE" == "by-run" ]]; then
  echo
  echo "By run:"
  printf "  %-19s  %-9s  %-22s  %-26s  %8s %8s  %9s\n" \
    "timestamp" "role" "phase" "model" "in_tok" "out_tok" "cost"
  while IFS=$'\t' read -r ts role phase model it ot cost; do
    printf "  %-19s  %-9s  %-22s  %-26s  %8d %8d  \$%8.4f\n" \
      "$ts" "$role" "$phase" "$model" "$it" "$ot" "$cost"
  done < "$RUNS_TMP"
fi

echo
awk -F'\t' '{ t+=$7; it+=$5; ot+=$6 } END{
  printf "================================================================\n";
  printf " TOTAL: %d input tok + %d output tok  ->  $%.4f (estimated)\n", it, ot, t;
  printf "================================================================\n" }' "$RUNS_TMP"
