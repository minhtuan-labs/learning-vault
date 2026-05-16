#!/usr/bin/env bash
set -euo pipefail

# v10.18 — Robustly write the user's project idea into PRODUCT_IDEA.md.
#
# Why this exists: on fresh Claude sessions, the Write tool sometimes
# fails to create PRODUCT_IDEA.md (path/permission edge cases). Using
# this helper via the Bash tool sidesteps the issue entirely — it just
# reads stdin and writes it to the file using plain shell I/O.
#
# Usage:
#   echo "idea text" | bash scripts/set_product_idea.sh
#   bash scripts/set_product_idea.sh < idea.txt
#   bash scripts/set_product_idea.sh "literal idea text as arg"
#
# Output: path + byte count for confirmation.

OUTFILE="PRODUCT_IDEA.md"

if [[ $# -gt 0 ]]; then
  # Literal arg mode (when the caller has the idea as a single string).
  printf '%s\n' "$1" > "$OUTFILE"
else
  # Stdin mode (when the caller pipes the idea in).
  cat > "$OUTFILE"
fi

BYTES=$(wc -c < "$OUTFILE" | tr -d ' ')
echo "✓ PRODUCT_IDEA.md written (${BYTES} bytes)"
echo "  Path: $(pwd)/$OUTFILE"
