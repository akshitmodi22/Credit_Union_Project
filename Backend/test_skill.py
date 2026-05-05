# ═══════════════════════════════════════════════════════════════
# test_skill.py — Validate all Code Engine endpoints
# Run: python test_skill.py
# ═══════════════════════════════════════════════════════════════

import requests
import json

BASE_URL = "https://your-skill-url.codeengine.appdomain.cloud"

PASS = "✓ PASS"
FAIL = "✗ FAIL"

def test(name, response, check_key=None, check_value=None):
    status = response.status_code
    try:
        data = response.json()
    except:
        data = {}

    ok = status == 200
    if check_key:
        ok = ok and data.get(check_key) == check_value

    icon = PASS if ok else FAIL
    print(f"{icon} {name}")
    if not ok:
        print(f"     Status: {status}")
        print(f"     Response: {json.dumps(data, indent=2)[:200]}")
    return data


print("\n" + "="*55)
print("  CREDIT UNION SKILL — ENDPOINT VALIDATION")
print("="*55 + "\n")

# ── Test 1: Health ─────────────────────────────────────────────
print("─── Basic Tests ───────────────────────────────────────")
r = requests.get(f"{BASE_URL}/health")
test("Health check", r, "status", "ok")

# ── Test 2: Available filters ──────────────────────────────────
r = requests.get(f"{BASE_URL}/available-filters?model=attrition")
test("Available filters", r, "status", "success")

# ── Test 3: Model health ───────────────────────────────────────
r = requests.get(f"{BASE_URL}/model-health")
test("Model health check", r, "status", "success")

# ── Test 4: Smart query — no filters ──────────────────────────
print("\n─── Smart Query Tests ─────────────────────────────────")
r = requests.post(f"{BASE_URL}/smart-query", json={
    "model" : "attrition",
    "top_n" : 20
})
data = test("Smart query — no filter top 20", r, "status", "success")
if data:
    v = data.get("validation", {})
    print(f"     Members returned : {data.get('summary', {}).get('total_returned', 0)}")
    print(f"     All valid        : {v.get('all_valid', False)}")
    print(f"     Excel URL        : {'✓' if data.get('downloads', {}).get('excel_url') else '✗'}")
    print(f"     PDF URL          : {'✓' if data.get('downloads', {}).get('pdf_url') else '✗'}")

# ── Test 5: Smart query — with branch filter ───────────────────
r = requests.post(f"{BASE_URL}/smart-query", json={
    "model"  : "attrition",
    "branch" : "Hartford",
    "tier"   : "High",
    "top_n"  : 100
})
data = test("Smart query — Hartford High top 100", r, "status", "success")
if data:
    v = data.get("validation", {})
    print(f"     Members returned    : {data.get('summary', {}).get('total_returned', 0)}")
    print(f"     Count correct       : {v.get('count', {}).get('passed', False)}")
    print(f"     Branch filter ok    : {v.get('branch', {}).get('passed', False)}")
    print(f"     Tier filter ok      : {v.get('tier', {}).get('passed', False)}")
    print(f"     Sorted correctly    : {v.get('sorted', {}).get('passed', False)}")
    print(f"     All valid           : {v.get('all_valid', False)}")

# ── Test 6: Smart query — loan model ──────────────────────────
r = requests.post(f"{BASE_URL}/smart-query", json={
    "model" : "loan",
    "tier"  : "High",
    "top_n" : 50
})
data = test("Smart query — loan High top 50", r, "status", "success")
if data:
    print(f"     Members returned : {data.get('summary', {}).get('total_returned', 0)}")

# ── Test 7: Smart query — propensity with county ───────────────
r = requests.post(f"{BASE_URL}/smart-query", json={
    "model"  : "propensity",
    "county" : "Hartford",
    "tier"   : "High"
})
data = test("Smart query — propensity Hartford county", r, "status", "success")
if data:
    print(f"     Members returned : {data.get('summary', {}).get('total_returned', 0)}")

# ── Test 8: Smart query — life stage filter ────────────────────
r = requests.post(f"{BASE_URL}/smart-query", json={
    "model"      : "attrition",
    "life_stage" : "retired",
    "tier"       : "High"
})
data = test("Smart query — retired members High risk", r, "status", "success")
if data:
    print(f"     Members returned : {data.get('summary', {}).get('total_returned', 0)}")

# ── Test 9: Smart query — min probability ─────────────────────
r = requests.post(f"{BASE_URL}/smart-query", json={
    "model"    : "attrition",
    "min_prob" : 0.80
})
data = test("Smart query — above 80% risk", r, "status", "success")
if data:
    v = data.get("validation", {})
    print(f"     Members returned : {data.get('summary', {}).get('total_returned', 0)}")
    print(f"     Min prob ok      : {v.get('min_prob', {}).get('passed', False)}")

# ── Test 10: Chart ─────────────────────────────────────────────
print("\n─── Chart Tests ────────────────────────────────────────")
r = requests.post(f"{BASE_URL}/generate-chart", json={
    "model"    : "attrition",
    "group_by" : "branch_assignment",
    "tier"     : "High"
})
data = test("Chart — attrition by branch", r, "status", "success")
if data:
    print(f"     Top branch  : {data.get('top_group', '')}")
    print(f"     Top count   : {data.get('top_count', 0)}")
    print(f"     Chart URL   : {'✓' if data.get('chart_url') else '✗'}")

r = requests.post(f"{BASE_URL}/generate-chart", json={
    "model"    : "attrition",
    "group_by" : "age_band",
    "tier"     : "High"
})
data = test("Chart — attrition by age band", r, "status", "success")

r = requests.post(f"{BASE_URL}/generate-chart", json={
    "model"    : "propensity",
    "group_by" : "income_band",
    "tier"     : "High"
})
data = test("Chart — propensity by income band", r, "status", "success")

# ── Test 11: Unified report ────────────────────────────────────
print("\n─── Unified Report Tests ───────────────────────────────")
r = requests.post(f"{BASE_URL}/unified-report", json={})
data = test("Unified report — all members", r, "status", "success")
if data:
    print(f"     Total members    : {data.get('total_members', 0)}")
    print(f"     Priority actions : {data.get('priority_actions', 0)}")
    print(f"     Excel URL        : {'✓' if data.get('downloads', {}).get('excel_url') else '✗'}")

r = requests.post(f"{BASE_URL}/unified-report", json={
    "branch": "Hartford"
})
data = test("Unified report — Hartford branch", r, "status", "success")
if data:
    print(f"     Total members    : {data.get('total_members', 0)}")
    print(f"     Priority actions : {data.get('priority_actions', 0)}")

# ── Summary ────────────────────────────────────────────────────
print("\n" + "="*55)
print("  VALIDATION COMPLETE")
print("="*55)
print("\nIf all tests passed — register openapi.yaml in Orchestrate!")
print("If any failed — check Code Engine logs:\n")
print("  ibmcloud ce app logs --name cu-credit-union-skill")
