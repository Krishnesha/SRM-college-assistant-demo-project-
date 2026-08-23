#!/usr/bin/env bash

# CampusAI One-Click Launcher
echo "=================================================="
echo "🎓 Starting CampusAI — Your College Assistant"
echo "=================================================="

# 1. Run Automated Unit Tests
echo "🧪 Running Automated Tests..."
python3 -m unittest tests/test_campus_ai.py -v

if [ $? -ne 0 ]; then
  echo "❌ Unit tests failed! Please check errors before running server."
  exit 1
fi

echo "✅ All Unit Tests Passed Cleanly!"
echo "--------------------------------------------------"

# 2. Kill lingering port 8000 process if present
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# 3. Launch CampusAI Server
echo "🚀 Starting CampusAI Local Server on http://localhost:8000..."
python3 backend/api/server.py 8000
