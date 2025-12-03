import json, sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE = "http://localhost:8000/v1/model"

ok = 0
bad = 0

def say_ok(name, val):
    global ok
    print(f"✅ {name}: {val}")
    ok += 1

def say_bad(name, msg):
    global bad
    print(f"❌ {name}: {msg}")
    bad += 1

def GET(path):
    try:
        with urlopen(BASE + path, timeout=10) as r:
            return r.getcode(), r.read().decode()
    except HTTPError as e:
        return e.code, e.read().decode()
    except URLError as e:
        return 0, str(e)

def POST(path, payload: dict):
    data = json.dumps(payload).encode()
    req = Request(BASE + path, data=data, headers={"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=10) as r:
            return r.getcode(), r.read().decode()
    except HTTPError as e:
        return e.code, e.read().decode()
    except URLError as e:
        return 0, str(e)

# 1) health.mode == mock
code, body = GET("/health")
if code == 200:
    mode = json.loads(body).get("mode")
    say_ok("health.mode", mode) if mode == "mock" else say_bad("health.mode", f"got={mode} expected=mock")
else:
    say_bad("health", f"HTTP {code} body={body}")

# 2) scenarios.count == 4
code, body = GET("/scenarios")
if code == 200:
    try:
        count = len(json.loads(body))
        say_ok("scenarios.count", count) if count == 4 else say_bad("scenarios.count", f"got={count} expected=4")
    except Exception as e:
        say_bad("scenarios.parse", f"{e}; body={body}")
else:
    say_bad("scenarios", f"HTTP {code} body={body}")

# 3) estimate.tco_12mo == 3540.0
code, body = POST("/estimate", {"num_servers": 12, "storage_tb": 7.5, "monthly_bandwidth_tb": 2.0, "region": "us-east-1"})
if code == 200:
    try:
        tco = json.loads(body)["tco_12mo"]
        say_ok("estimate.tco_12mo", tco) if str(tco) == "3540.0" else say_bad("estimate.tco_12mo", f"got={tco} expected=3540.0")
    except Exception as e:
        say_bad("estimate.parse", f"{e}; body={body}")
else:
    say_bad("estimate", f"HTTP {code} body={body}")

# 4) what-if scenarios (rounded comparisons)
tests = {
    "baseline": "1000.00",
    "rehost_aws": "899.96",
    "refactor_azure": "860.04",
    "replatform_gcp": "800.00",
}
for scen, exp in tests.items():
    code, body = POST("/whatif", {"scenario": scen})
    if code == 200:
        try:
            tco = float(json.loads(body)["tco_12mo"])
            got = f"{tco:.2f}"
            say_ok(f"whatif.{scen}", got) if got == exp else say_bad(f"whatif.{scen}", f"got={got} expected={exp}")
        except Exception as e:
            say_bad(f"whatif.{scen}.parse", f"{e}; body={body}")
    else:
        say_bad(f"whatif.{scen}", f"HTTP {code} body={body}")

print()
if bad == 0:
    print(f"✅ Phase 8 Verification: ALL {ok} check(s) passed.")
    sys.exit(0)
else:
    print(f"❌ Phase 8 Verification: {bad} failed, {ok} passed.")
    sys.exit(1)
