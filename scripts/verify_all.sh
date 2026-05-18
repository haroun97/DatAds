#!/usr/bin/env bash
# Quick automated verification — run manual_verification_guide.md for full checks.
set -euo pipefail
cd "$(dirname "$0")/.."

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'
pass() { echo -e "${GREEN}PASS${NC} $1"; }
fail() { echo -e "${RED}FAIL${NC} $1"; FAILED=1; }
warn() { echo -e "WARN $1"; }

FAILED=0
API_BASE="${API_BASE:-https://datads-mock-ad-apis.happygrass-47d99234.germanywestcentral.azurecontainerapps.io}"

echo "========== DatAds Verification =========="

# --- Part 1 files ---
test -f part_1/system_design.png && pass "part_1/system_design.png" || fail "part_1/system_design.png"
test -f part_1/README.md && pass "part_1/README.md" || fail "part_1/README.md"
test -f part_2/README.md && pass "part_2/README.md" || fail "part_2/README.md"
test -f part_3/README.md && pass "part_3/README.md" || fail "part_3/README.md"
test -f README.md && pass "README.md" || fail "README.md"
test -f requirements.txt && pass "requirements.txt" || fail "requirements.txt"

# --- Part 2 code ---
test -f app/pollers/facebook.py && pass "Facebook poller" || fail "Facebook poller"
test -f app/services/metrics_service.py && pass "Metrics service" || fail "Metrics service"
test -f scripts/ingest_facebook.py && pass "Ingestion script" || fail "Ingestion script"

# --- Part 3 code ---
test -f app/api/routes.py && pass "API routes" || fail "API routes"
test -f app/main.py && pass "FastAPI main" || fail "FastAPI main"

# --- Mock API ---
if curl -sf "$API_BASE/health" | grep -q healthy; then
  pass "Mock API /health"
else
  fail "Mock API /health"
fi

# --- Tests ---
if [[ -d venv ]]; then
  source venv/bin/activate
fi
if pytest -q 2>/dev/null; then
  pass "pytest (13 tests)"
else
  fail "pytest"
fi

# --- Local API (optional) ---
if curl -sf http://127.0.0.1:8000/health | grep -q ok 2>/dev/null; then
  pass "Local API /health"
  if curl -sf "http://127.0.0.1:8000/api/performance?platform=facebook" | grep -q total_impressions; then
    pass "Local API /api/performance"
  else
    warn "Local API /api/performance — empty DB? Run ingestion first"
  fi
else
  warn "Local API not running — start: uvicorn app.main:app --reload"
fi

# --- Git (submission) ---
if git rev-parse --is-inside-work-tree &>/dev/null; then
  pass "Git repository initialized"
else
  warn "Git not initialized (required for Part 4 submission)"
fi

echo "========================================="
if [[ "${FAILED:-0}" -eq 0 ]]; then
  echo -e "${GREEN}All automated checks passed.${NC}"
  echo "Continue with documents/manual_verification_guide.md for manual steps."
else
  echo -e "${RED}Some checks failed.${NC}"
  exit 1
fi
