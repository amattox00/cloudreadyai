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
  echo " CloudReadyAI Phase A3 — Login → Diagrams UX Verification"
  echo "------------------------------------------------------------"
}

print_footer() {
  echo
  echo "------------------------------------------------------------"
  echo " Phase A3 Verification Summary"
  echo "------------------------------------------------------------"
  echo "  Passed checks: $PASS_COUNT"
  echo "  Failed checks: $FAIL_COUNT"
  if [ "$FAIL_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}Some checks failed. Review messages above and adjust.${RESET}"
  else
    echo -e "${GREEN}All Phase A3 checks PASSED.${RESET}"
  fi
}

print_header

# 1) Backend health
if curl -sS http://localhost:8000/healthz >/dev/null 2>&1; then
  pass "Backend /healthz is responding"
else
  fail "Backend /healthz is NOT responding"
fi

# 2) OpenAPI reachable
if curl -sS http://localhost:8000/openapi.json >/dev/null 2>&1; then
  pass "/openapi.json is reachable"
else
  fail "/openapi.json is NOT reachable"
fi

DIAGRAMS_PAGE="frontend/src/pages/DiagramsPage.tsx"

if [ ! -f "$DIAGRAMS_PAGE" ]; then
  fail "DiagramsPage.tsx not found at $DIAGRAMS_PAGE"
  print_footer
  exit 1
fi

# 3) Ensure old dev-only UI strings are gone
if grep -q "Access Token:" "$DIAGRAMS_PAGE"; then
  fail "Found legacy 'Access Token:' debug UI in DiagramsPage.tsx"
else
  pass "Legacy 'Access Token:' debug UI is removed"
fi

if grep -q "Who am I?" "$DIAGRAMS_PAGE"; then
  fail "Found legacy 'Who am I?' debug UI in DiagramsPage.tsx"
else
  pass "Legacy 'Who am I?' debug UI is removed"
fi

# 4) Ensure new login gating exists
if grep -q "if (!isLoggedIn)" "$DIAGRAMS_PAGE"; then
  pass "Login gating (if !isLoggedIn) is present"
else
  fail "Login gating (if !isLoggedIn) not found in DiagramsPage.tsx"
fi

if grep -q "function handleLogin" "$DIAGRAMS_PAGE" || grep -q "async function handleLogin" "$DIAGRAMS_PAGE"; then
  pass "handleLogin function is present"
else
  fail "handleLogin function not found in DiagramsPage.tsx"
fi

print_footer
