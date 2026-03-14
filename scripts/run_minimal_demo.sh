#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="$ROOT_DIR"

HOST="${PHYSCLAW_NODE_SERVER_HOST:-127.0.0.1}"
PORT="${PHYSCLAW_NODE_SERVER_PORT:-8765}"

echo "[run] PhysClaw minimal demo"
echo "[run] Node Server: http://${HOST}:${PORT}"
if command -v openclaw >/dev/null 2>&1; then
  echo "[run] openclaw detected: $(openclaw --version | head -n 1)"
else
  echo "[run] openclaw not found, demo will still run with local routing"
fi

python3 "$ROOT_DIR/scripts/minimal_openclaw_node_demo.py"
