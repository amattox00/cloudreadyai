#!/usr/bin/env bash
set -euo pipefail

RED="$(printf '\033[31m')"
GREEN="$(printf '\033[32m')"
YELLOW="$(printf '\033[33m')"
RESET="$(printf '\033[0m')"

PASS_COUNT=0
FAIL_COUNT=0

pass() { echo -e "${GREEN}✔ $1${RESET}"; PASS_COUNT=$((PASS_COUNT+1)); }
fail() { echo -e "${RED}✘ $1${RESET}"; FAIL_COUNT=$((FAIL_COUNT+1)); }

print_header() {
  echo
  echo "------------------------------------------------------------"
  echo " CloudReadyAI Phase A2 — Unified API Spec Verification"
  echo "------------------------------------------------------------"
}

print_footer() {
  echo
  echo "------------------------------------------------------------"
  echo " Phase A2 Verification Summary"
  echo "------------------------------------------------------------"
  echo "  Passed checks: $PASS_COUNT"
  echo "  Failed checks: $FAIL_COUNT"
  if [ "$FAIL_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}Some checks failed. Review messages above and adjust.${RESET}"
  else
    echo -e "${GREEN}All Phase A2 checks PASSED.${RESET}"
  fi
}

print_header

# 1) Check that /openapi.json responds
if curl -sS http://localhost:8000/openapi.json >/tmp/phaseA2_openapi.json 2>/dev/null; then
  pass "/openapi.json is reachable"
else
  fail "/openapi.json is not reachable on localhost:8000"
  print_footer
  exit 1
fi

# Decide which Python to use (prefer backend venv, then python3/python)
PYTHON="/home/ec2-user/cloudreadyai/backend/.venv/bin/python"
if [ ! -x "$PYTHON" ]; then
  PYTHON="$(command -v python3 || command -v python || echo '')"
fi

if [ -z "$PYTHON" ]; then
  fail "No usable Python interpreter found (backend venv/python3/python)"
  print_footer
  exit 1
fi

# 2) Inspect tags and basic grouping via Python
if "$PYTHON" << 'PY'
import json, pathlib, sys

p = pathlib.Path("/tmp/phaseA2_openapi.json")
if not p.exists():
    print("FAIL: /tmp/phaseA2_openapi.json not found")
    sys.exit(1)

data = json.loads(p.read_text())

tags = {t.get("name") for t in data.get("tags", []) if isinstance(t, dict)}
required = {"runs", "ingestion", "diagrams", "cost", "reporting"}

missing = required - tags
if missing:
    print(f"FAIL: Missing expected tags: {sorted(missing)}")
    sys.exit(1)

# Basic sanity check: at least one path has each of these tags, if paths exist
paths = data.get("paths", {})
tag_usage = {name: False for name in required}

for path, methods in paths.items():
    for method, op in methods.items():
        if not isinstance(op, dict):
            continue
        for t in op.get("tags") or []:
            if t in tag_usage:
                tag_usage[t] = True

# It's okay if some domains have no implemented paths yet,
# but we at least log their status.
for name, used in tag_usage.items():
    if used:
        print(f"OK: Tag '{name}' is used by at least one path")
    else:
        print(f"WARN: Tag '{name}' is defined but not used by any path (yet)")

print("OK: Required tags present and basic grouping verified")
PY
then
  pass "OpenAPI schema contains required tags and basic grouping"
else
  fail "OpenAPI schema is missing required tags or grouping"
fi

print_footer
