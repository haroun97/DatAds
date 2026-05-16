#!/usr/bin/env bash
# Local dev setup without Docker — uses SQLite.
set -euo pipefail
cd "$(dirname "$0")/.."

export DATABASE_URL="${DATABASE_URL:-sqlite:///./datads.db}"

if [[ ! -d venv ]]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt

alembic upgrade head
python scripts/ingest_facebook.py

echo ""
echo "Starting API on http://127.0.0.1:8000 (Ctrl+C to stop)"
echo "Docs: http://127.0.0.1:8000/docs"
exec uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
