#!/usr/bin/env bash
set -u

HOST="127.0.0.1"
PORT="8000"
BASE="http://$HOST:$PORT"
REDIS_CLI="$(command -v redis-cli || command -v redis6-cli || true)"
CURL_MAX_FIRST=12
CURL_MAX_SECOND=8
TOTAL_FAILS=0
TMPDIR="$(mktemp -d)"
HEAD1="$TMPDIR/h1.txt"
BODY1="$TMPDIR/b1.txt"
HEAD2="$TMPDIR/h2.txt"
BODY2="$TMPDIR/b2.txt"
URL="$BASE/v1/providers/prices?provider=AWS&region=us-east-1&service=ec2"
CACHE_KEY_PATTERN="phase5:prices:AWS:us-east-1:ec2"

pass() { echo -e "✅ $*"; }
fail() { echo -e "❌ $*"; TOTAL_FAILS=$((TOTAL_FAILS+1)); }
banner() { echo -e "\n==== $* ===="; }

cleanup() { rm -rf "$TMPDIR"; }
trap cleanup EXIT

# Helper: parse HTTP status from headers (HTTP/1.1 or HTTP/2)
http_code() { awk '/^HTTP\//{c=$2} END{print c+0}' "$1" 2>/dev/null; }

# Helper: current service "since" timestamp for scoped log checks
service_since() {
  systemctl show cloudready-backend -p ActiveEnterTimestamp --value 2>/dev/null
}

banner "Step 0: /healthz"
if curl -fsS "$BASE/healthz" >/dev/null; then
  pass "/healthz reachable"
else
  fail "/healthz failed"
fi

banner "Prep: ensure first call is a MISS by purging cache key"
if [[ -n "$REDIS_CLI" ]]; then
  if "$REDIS_CLI" -h 127.0.0.1 -p 6379 ping >/dev/null 2>&1; then
    # Best-effort delete of the known key/pattern
    KEYS=$("$REDIS_CLI" -h 127.0.0.1 -p 6379 KEYS "$CACHE_KEY_PATTERN" 2>/dev/null || true)
    if [[ -n "$KEYS" ]]; then
      echo "$KEYS" | xargs -r "$REDIS_CLI" -h 127.0.0.1 -p 6379 DEL >/dev/null 2>&1 || true
      pass "Purged existing cache keys for first-call MISS"
    else
      pass "No existing cache keys (clean start)"
    fi
  else
    fail "Redis unreachable during prep purge (will continue)"
  fi
else
  fail "redis-cli not found (will continue)"
fi

banner "Step 1: First /v1/providers/prices (MISS)"
if curl -sS --max-time "$CURL_MAX_FIRST" -D "$HEAD1" -o "$BODY1" "$URL"; then
  CODE="$(http_code "$HEAD1")"
  if [[ "$CODE" -eq 200 ]]; then
    pass "HTTP 200 on first call"
  else
    fail "HTTP $CODE on first call"
  fi
  XC="$(grep -i '^X-Cache:' "$HEAD1" | awk -F': ' '{print $2}' | tr -d '\r')"
  if [[ "$XC" == MISS* ]]; then
    pass "MISS detected on first call"
  else
    fail "Expected MISS on first call; got: ${XC:-'(none)'}"
  fi
else
  fail "First call timed out"
fi

banner "Step 2: Second call (HIT)"
if curl -sS --max-time "$CURL_MAX_SECOND" -D "$HEAD2" -o "$BODY2" "$URL"; then
  CODE="$(http_code "$HEAD2")"
  if [[ "$CODE" -eq 200 ]]; then
    pass "HTTP 200 on second call"
  else
    fail "HTTP $CODE on second call"
  fi
  XC="$(grep -i '^X-Cache:' "$HEAD2" | awk -F': ' '{print $2}' | tr -d '\r')"
  if [[ "$XC" == HIT* ]]; then
    pass "HIT detected on second call"
  else
    fail "Expected HIT on second call; got: ${XC:-'(none)'}"
  fi
else
  fail "Second call timed out"
fi

banner "Step 3: Redis KEY check"
if [[ -z "$REDIS_CLI" ]]; then
  fail "redis-cli missing"
else
  if "$REDIS_CLI" -h 127.0.0.1 -p 6379 ping >/dev/null 2>&1; then
    pass "Redis online"
    KEY="$("$REDIS_CLI" -h 127.0.0.1 -p 6379 KEYS "$CACHE_KEY_PATTERN" | head -n 1)"
    [[ -n "$KEY" ]] && pass "Key found: $KEY" || fail "No phase5 cache key created"
  else
    fail "Redis unreachable"
  fi
fi

banner "Step 4: Other endpoints"
PAY='{"vcpus":8,"memory_gb":32,"os":"linux","storage_gb":500}'
curl -fsS -o /dev/null "$BASE/v1/diagram" && pass "/v1/diagram OK" || fail "/v1/diagram"
curl -fsS -H 'Content-Type: application/json' -d "$PAY" -o /dev/null "$BASE/v1/match/services" && pass "/v1/match/services OK" || fail "/v1/match/services"
curl -fsS -H 'Content-Type: application/json' -d "$PAY" -o /dev/null "$BASE/v1/cost/compare" && pass "/v1/cost/compare OK" || fail "/v1/cost/compare"
curl -fsS -H 'Content-Type: application/json' -d "$PAY" -o /dev/null "$BASE/v1/recommend" && pass "/v1/recommend OK" || fail "/v1/recommend"

banner "Step 5: Stability (only since current start)"
SINCE="$(service_since)"
if [[ -z "$SINCE" ]]; then
  fail "Could not determine service start time"
else
  if journalctl -u cloudready-backend --since "$SINCE" | grep -qi 'oom-kill'; then
    fail "OOM detected since $SINCE"
  else
    pass "No OOM since current start ($SINCE)"
  fi
fi
systemctl is-active --quiet cloudready-backend && pass "Backend active" || fail "Backend NOT active"

banner "SUMMARY"
if [[ "$TOTAL_FAILS" -eq 0 ]]; then
  pass "ALL CHECKS PASSED ✅"
else
  fail "$TOTAL_FAILS ISSUE(S) FAILED ❌"
fi
