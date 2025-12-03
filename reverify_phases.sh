#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

PHASES=(1 2 3 4 5 6 7 8)

for p in "${PHASES[@]}"; do
  SCRIPT="phase${p}_verify.sh"
  echo "============================"
  echo " Phase $p – $SCRIPT"
  echo "============================"
  if [[ -x "$SCRIPT" ]]; then
    ./"$SCRIPT" || echo "Phase $p verification script returned non-zero exit code"
  else
    echo "Skipping Phase $p – $SCRIPT not found or not executable"
  fi
  echo
done

echo "============================"
echo " Phase 7B – phase7b_verify.sh"
echo "============================"
if [[ -x "phase7b_verify.sh" ]]; then
  ./phase7b_verify.sh || echo "Phase 7B verification script returned non-zero exit code"
else
  echo "Skipping Phase 7B – phase7b_verify.sh not found or not executable"
fi
echo
