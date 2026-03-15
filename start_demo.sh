#!/usr/bin/env bash
# ============================================================
#  Neos Autonomous Dev Squad — Demo Launcher
#  Starts FastAPI backend + Streamlit frontend, then exposes
#  port 8501 to the internet via ngrok.
#  Usage: bash start_demo.sh
# ============================================================

set -euo pipefail

# ── Colours ──────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

# ── Locate virtual-env Python / pip executables ───────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="${SCRIPT_DIR}/venv/bin/python"
VENV_STREAMLIT="${SCRIPT_DIR}/venv/bin/streamlit"
VENV_UVICORN="${SCRIPT_DIR}/venv/bin/uvicorn"

# Windows Git Bash / WSL fallback paths
if [[ ! -f "$VENV_PYTHON" ]]; then
  VENV_PYTHON="${SCRIPT_DIR}/venv/Scripts/python"
  VENV_STREAMLIT="${SCRIPT_DIR}/venv/Scripts/streamlit"
  VENV_UVICORN="${SCRIPT_DIR}/venv/Scripts/uvicorn"
fi

# ── Pre-flight checks ─────────────────────────────────────────
echo -e "${BOLD}${CYAN}"
echo "  ███╗   ██╗███████╗ ██████╗ ███████╗"
echo "  ████╗  ██║██╔════╝██╔═══██╗██╔════╝"
echo "  ██╔██╗ ██║█████╗  ██║   ██║███████╗"
echo "  ██║╚██╗██║██╔══╝  ██║   ██║╚════██║"
echo "  ██║ ╚████║███████╗╚██████╔╝███████║"
echo "  ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚══════╝"
echo -e "${RESET}"
echo -e "${BOLD} Neos Autonomous Dev Squad — Mission Launcher${RESET}"
echo -e " ─────────────────────────────────────────────"

check_command() {
  if ! command -v "$1" &>/dev/null; then
    echo -e "${RED}[ERROR]${RESET} '$1' not found. $2"
    exit 1
  fi
}

check_command ngrok       "Install from https://ngrok.com/download and run: ngrok config add-authtoken <TOKEN>"
check_command "$VENV_UVICORN"   "Activate venv and run: pip install -r requirements.txt"
check_command "$VENV_STREAMLIT" "Activate venv and run: pip install streamlit"

if [[ ! -f "${SCRIPT_DIR}/.env" ]]; then
  echo -e "${YELLOW}[WARN]${RESET}  No .env file found. Create one with GOOGLE_API_KEY=<your-key>"
fi

echo -e "${GREEN}[OK]${RESET}    All pre-flight checks passed."
echo ""

# ── PID tracking for clean teardown ──────────────────────────
FASTAPI_PID=""
STREAMLIT_PID=""

cleanup() {
  echo ""
  echo -e "${YELLOW}[SHUTDOWN]${RESET} Ctrl+C detected — tearing down demo stack..."

  if [[ -n "$FASTAPI_PID" ]] && kill -0 "$FASTAPI_PID" 2>/dev/null; then
    echo -e "${YELLOW}[SHUTDOWN]${RESET} Stopping FastAPI backend (PID $FASTAPI_PID)..."
    kill "$FASTAPI_PID" 2>/dev/null
    wait "$FASTAPI_PID" 2>/dev/null || true
  fi

  if [[ -n "$STREAMLIT_PID" ]] && kill -0 "$STREAMLIT_PID" 2>/dev/null; then
    echo -e "${YELLOW}[SHUTDOWN]${RESET} Stopping Streamlit frontend (PID $STREAMLIT_PID)..."
    kill "$STREAMLIT_PID" 2>/dev/null
    wait "$STREAMLIT_PID" 2>/dev/null || true
  fi

  echo -e "${GREEN}[DONE]${RESET}   All processes stopped. Mission debrief complete."
  exit 0
}

# Register cleanup on SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM

# ── Start FastAPI backend ─────────────────────────────────────
echo -e "${CYAN}[1/3]${RESET} Starting FastAPI backend on port 8000..."
cd "$SCRIPT_DIR"

"$VENV_UVICORN" worker:app --host 0.0.0.0 --port 8000 \
  >> "${SCRIPT_DIR}/logs/backend.log" 2>&1 &
FASTAPI_PID=$!

echo -e "${GREEN}[OK]${RESET}    FastAPI running (PID $FASTAPI_PID) → http://localhost:8000"
echo -e "        Logs: logs/backend.log"

# Give it a moment to boot
sleep 2

# ── Start Streamlit frontend ──────────────────────────────────
echo -e "${CYAN}[2/3]${RESET} Starting Streamlit frontend on port 8501..."

"$VENV_STREAMLIT" run app_ui.py \
  --server.port 8501 \
  --server.headless true \
  --browser.gatherUsageStats false \
  >> "${SCRIPT_DIR}/logs/frontend.log" 2>&1 &
STREAMLIT_PID=$!

echo -e "${GREEN}[OK]${RESET}    Streamlit running (PID $STREAMLIT_PID) → http://localhost:8501"
echo -e "        Logs: logs/frontend.log"

# Give it a moment to boot
sleep 3

# ── Start Ngrok tunnel (foreground) ──────────────────────────
echo -e "${CYAN}[3/3]${RESET} Opening ngrok tunnel to port 8501..."
echo ""
echo -e " ${BOLD}════════════════════════════════════════════${RESET}"
echo -e " ${BOLD}  Your public demo URL will appear below:   ${RESET}"
echo -e " ${BOLD}════════════════════════════════════════════${RESET}"
echo ""

# Ensure log directory exists
mkdir -p "${SCRIPT_DIR}/logs"

ngrok http 8501 --log=stdout

# If ngrok exits (user pressed Ctrl+C), run cleanup
cleanup
