import streamlit as st
import requests
import uuid
import time
import os
from datetime import datetime

# ── Constants ──────────────────────────────────────────────────────────────────
# When running inside Docker Compose, BACKEND_URL is set to http://backend:8000
# When running locally, it falls back to http://localhost:8000
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000").rstrip("/")

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Neos Autonomous Dev Squad - Mission Control",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Import fonts */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=JetBrains+Mono:wght@400;600&family=Inter:wght@400;500;600&display=swap');

/* Root variables */
:root {
    --bg-dark: #0a0e1a;
    --bg-panel: #0f1629;
    --bg-terminal: #05090f;
    --border-glow: #1e3a5f;
    --accent-blue: #00d4ff;
    --accent-green: #00ff88;
    --accent-orange: #ff8c00;
    --accent-red: #ff3b5c;
    --text-dim: #4a6fa5;
    --text-muted: #6b7a99;
}

/* Hide Streamlit branding */
#MainMenu, footer, header {visibility: hidden;}

/* App background */
.stApp {
    background: var(--bg-dark);
    background-image:
        radial-gradient(ellipse at 20% 50%, rgba(0, 56, 120, 0.15) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 20%, rgba(0, 100, 180, 0.10) 0%, transparent 50%);
}

/* Main content */
.block-container {
    padding: 2rem 4rem !important;
    max-width: 1200px !important;
}

/* Title styling */
.hero-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 2.2rem;
    font-weight: 900;
    letter-spacing: 0.08em;
    background: linear-gradient(90deg, #00d4ff, #0077ff, #00ff88);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0;
    line-height: 1.2;
}

.hero-sub {
    font-family: 'Inter', sans-serif;
    color: var(--text-muted);
    font-size: 0.85rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    margin-top: 4px;
    margin-bottom: 1.5rem;
}

/* Input area */
.stTextArea textarea {
    background: var(--bg-panel) !important;
    border: 1px solid var(--border-glow) !important;
    border-radius: 10px !important;
    color: #c9d8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1rem !important;
    padding: 16px !important;
    transition: border-color 0.3s;
}
.stTextArea textarea:focus {
    border-color: var(--accent-blue) !important;
    box-shadow: 0 0 20px rgba(0, 212, 255, 0.15) !important;
}
label[for], .stTextArea label {
    color: #7a9cc8 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
}

/* Deploy button */
.stButton > button {
    background: linear-gradient(135deg, #003580 0%, #0055cc 50%, #0077ff 100%) !important;
    color: white !important;
    border: 1px solid rgba(0, 212, 255, 0.3) !important;
    border-radius: 8px !important;
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    padding: 0.7rem 2.5rem !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(0, 85, 204, 0.4) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(0, 119, 255, 0.6) !important;
    border-color: var(--accent-blue) !important;
}
.stButton > button:active {
    transform: translateY(0px) !important;
}

/* Terminal window */
.terminal-window {
    background: var(--bg-terminal);
    border: 1px solid #1a2d4a;
    border-radius: 12px;
    overflow: hidden;
    box-shadow:
        0 0 40px rgba(0, 150, 255, 0.08),
        0 20px 60px rgba(0,0,0,0.6),
        inset 0 1px 0 rgba(255,255,255,0.04);
    margin-top: 1.5rem;
}

.terminal-titlebar {
    background: #0c1220;
    padding: 10px 16px;
    display: flex;
    align-items: center;
    gap: 8px;
    border-bottom: 1px solid #1a2d4a;
}

.dot { width: 12px; height: 12px; border-radius: 50%; }
.dot-red { background: #ff5f57; }
.dot-yellow { background: #ffbd2e; }
.dot-green { background: #28ca41; }

.terminal-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #3d5a80;
    margin-left: 10px;
    letter-spacing: 0.1em;
}

.terminal-body {
    padding: 20px 24px;
    min-height: 260px;
    max-height: 420px;
    overflow-y: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    line-height: 1.8;
}

/* Status badge */
.status-badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    margin-left: auto;
}
.badge-running { background: rgba(255, 140, 0, 0.15); color: #ff8c00; border: 1px solid #ff8c00; }
.badge-passed  { background: rgba(0, 255, 136, 0.12); color: #00ff88; border: 1px solid #00ff88; }
.badge-failed  { background: rgba(255, 59, 92, 0.12);  color: #ff3b5c; border: 1px solid #ff3b5c; }
.badge-idle    { background: rgba(74, 111, 165, 0.15); color: #4a6fa5; border: 1px solid #4a6fa5; }

/* Code output panel */
.code-panel {
    background: #0d1117;
    border: 1px solid rgba(0, 255, 136, 0.3);
    border-radius: 12px;
    padding: 1.5rem;
    margin-top: 1.5rem;
    box-shadow: 0 0 30px rgba(0, 255, 136, 0.06);
}
.code-panel-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.75rem;
    color: #00ff88;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

/* Stat cards */
.stat-row {
    display: flex;
    gap: 12px;
    margin-bottom: 1.5rem;
}
.stat-card {
    flex: 1;
    background: var(--bg-panel);
    border: 1px solid var(--border-glow);
    border-radius: 10px;
    padding: 16px;
    text-align: center;
}
.stat-value {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--accent-blue);
}
.stat-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.65rem;
    color: var(--text-muted);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 4px;
}

/* Divider */
.neos-divider {
    border: none;
    border-top: 1px solid #1a2d4a;
    margin: 1.5rem 0;
}
</style>
""", unsafe_allow_html=True)

POLL_INTERVAL = 1.5  # seconds

# ── Session state init ─────────────────────────────────────────────────────────
def _init_state():
    defaults = {
        "thread_id": None,
        "running": False,
        "logs": [],
        "last_status": None,
        "last_iterations": -1,
        "final_code": None,
        "deploy_count": 0,
        "start_time": None,
        "elapsed": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# ── Helper functions ───────────────────────────────────────────────────────────
def ts():
    return datetime.now().strftime("%H:%M:%S")

def make_log(icon, msg, color="#4fc3f7"):
    """Returns an HTML log line for the terminal."""
    return (
        f'<span style="color:#2e4a6e">[{ts()}]</span> '
        f'<span style="color:{color}">{icon} {msg}</span>'
    )

def submit_task(prompt: str):
    thread_id = f"mission-{uuid.uuid4().hex[:8]}"
    try:
        resp = requests.post(
            f"{BACKEND_URL}/task",
            json={"prompt": prompt, "thread_id": thread_id},
            timeout=10,
        )
        resp.raise_for_status()
        return thread_id
    except requests.exceptions.ConnectionError:
        st.error(f"Cannot reach backend at {BACKEND_URL}. Is the backend running?")
        return None
    except Exception as e:
        st.error(f"❌ Failed to submit task: {e}")
        return None

def poll_status(thread_id: str):
    try:
        resp = requests.get(f"{BACKEND_URL}/task/{thread_id}", timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None

# ── Layout ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">🛰️ NEOS AUTONOMOUS DEV SQUAD</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Mission Control · Real-Time Agent Orchestration</div>', unsafe_allow_html=True)

# Stat cards
elapsed = st.session_state.elapsed
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{st.session_state.deploy_count}</div>
        <div class="stat-label">Missions Deployed</div>
    </div>""", unsafe_allow_html=True)
with col2:
    iters = max(0, st.session_state.last_iterations)
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{iters}</div>
        <div class="stat-label">QA Iterations</div>
    </div>""", unsafe_allow_html=True)
with col3:
    elapsed_str = f"{int(elapsed)}s" if elapsed < 60 else f"{int(elapsed/60)}m {int(elapsed%60)}s"
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{elapsed_str if st.session_state.start_time else "--"}</div>
        <div class="stat-label">Elapsed Time</div>
    </div>""", unsafe_allow_html=True)
with col4:
    final_status = st.session_state.last_status or "idle"
    badge_cls = {
        "idle": "badge-idle",
        "pending": "badge-running",
        "failed": "badge-running",
        "passed": "badge-passed",
    }.get(final_status, "badge-idle")
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value" style="font-size:1rem; padding-top:6px">
            <span class="status-badge {badge_cls}">{final_status.upper()}</span>
        </div>
        <div class="stat-label">Last QA Status</div>
    </div>""", unsafe_allow_html=True)

st.markdown('<hr class="neos-divider">', unsafe_allow_html=True)

# Input + button
prompt_input = st.text_area(
    "🎯 Feature Request",
    placeholder='e.g. "Write a secure PHP login function with bcrypt password hashing."',
    height=120,
    key="prompt_input",
)

deploy_clicked = st.button("🚀 &nbsp; DEPLOY SQUAD", disabled=st.session_state.running)

# ── Deploy logic ───────────────────────────────────────────────────────────────
if deploy_clicked and prompt_input.strip():
    thread_id = submit_task(prompt_input.strip())
    if thread_id:
        st.session_state.thread_id = thread_id
        st.session_state.running = True
        st.session_state.deploy_count += 1
        st.session_state.start_time = time.time()
        st.session_state.elapsed = 0
        st.session_state.last_status = "pending"
        st.session_state.last_iterations = -1
        st.session_state.final_code = None
        st.session_state.logs = [
            make_log("🛰️", f"Mission #{st.session_state.deploy_count} initiated — thread: <b>{thread_id}</b>", "#00d4ff"),
            make_log("🧠", "Lead Agent: Receiving mission briefing...", "#a78bfa"),
            make_log("📡", "Polling backend for agent activity...", "#4a6fa5"),
        ]
        st.rerun()

elif deploy_clicked and not prompt_input.strip():
    st.warning("⚠️ Please enter a feature request first.")

# ── Terminal window ────────────────────────────────────────────────────────────
if st.session_state.logs or st.session_state.running:
    is_running = st.session_state.running
    badge_cls = "badge-running" if is_running else ("badge-passed" if st.session_state.last_status == "passed" else "badge-idle")
    badge_label = "RUNNING" if is_running else (st.session_state.last_status or "IDLE").upper()

    terminal_html = "\n".join(st.session_state.logs[-60:])  # keep last 60 lines

    st.markdown(f"""
    <div class="terminal-window">
      <div class="terminal-titlebar">
        <span class="dot dot-red"></span>
        <span class="dot dot-yellow"></span>
        <span class="dot dot-green"></span>
        <span class="terminal-label">AGENT LOG STREAM — {st.session_state.thread_id or "—"}</span>
        <span class="status-badge {badge_cls}" style="margin-left:auto">{badge_label}</span>
      </div>
      <div class="terminal-body" id="terminal-body">
        {terminal_html}
        {'<span style="color:#1e3a5f;animation:blink 1s step-end infinite">█</span>' if is_running else ''}
      </div>
    </div>
    <script>
      var t = document.getElementById("terminal-body");
      if(t) t.scrollTop = t.scrollHeight;
    </script>
    """, unsafe_allow_html=True)

# ── Polling loop ───────────────────────────────────────────────────────────────
if st.session_state.running and st.session_state.thread_id:
    time.sleep(POLL_INTERVAL)

    if st.session_state.start_time:
        st.session_state.elapsed = time.time() - st.session_state.start_time

    data = poll_status(st.session_state.thread_id)

    if data is None:
        # Task not yet registered in the checkpointer — still warming up
        st.session_state.logs.append(make_log("⏳", "Waiting for Lead Agent to initialize...", "#3b5580"))
    else:
        qa_status = data.get("qa_status", "pending")
        iterations = data.get("iterations", 0)

        # ── Detect new iteration ───────────────────────────────────────────────
        if iterations != st.session_state.last_iterations:
            if st.session_state.last_iterations == -1:
                # First real contact
                st.session_state.logs.append(make_log("🧠", "Lead Agent: Analyzing feature requirements...", "#a78bfa"))
                st.session_state.logs.append(make_log("📋", "Lead Agent: Decomposing task into sub-steps...", "#a78bfa"))
                st.session_state.logs.append(make_log("💻", "Coder Agent: Writing initial implementation...", "#60a5fa"))
                st.session_state.logs.append(make_log("🧪", "QA Agent: Preparing Docker sandbox...", "#fbbf24"))
            elif iterations > st.session_state.last_iterations:
                st.session_state.logs.append(make_log("🔧", f"Coder Agent: Applying fix — attempt #{iterations}...", "#f97316"))
                st.session_state.logs.append(make_log("🧪", "QA Agent: Re-running sandbox evaluation...", "#fbbf24"))

            st.session_state.last_iterations = iterations

        # ── Detect status change ───────────────────────────────────────────────
        if qa_status != st.session_state.last_status:
            if qa_status == "failed":
                exec_logs = (data.get("execution_logs") or "")[:300].replace("\n", " ")
                st.session_state.logs.append(make_log("❌", "QA SANDBOX: Execution FAILED.", "#ff3b5c"))
                if exec_logs:
                    st.session_state.logs.append(make_log("📄", f"Error log: {exec_logs}", "#ff7a8a"))
                st.session_state.logs.append(make_log("🔁", "Self-correction loop activating — routing back to Coder...", "#f97316"))

            elif qa_status == "passed":
                st.session_state.logs.append(make_log("✅", "QA SANDBOX: Code executed SUCCESSFULLY.", "#00ff88"))
                st.session_state.logs.append(make_log("💾", "Saver Agent: Persisting artifact to outputs/ directory...", "#00bcd4"))
                st.session_state.logs.append(make_log("🏁", f"Mission complete in {int(st.session_state.elapsed)}s with {iterations} QA iteration(s).", "#00d4ff"))
                st.session_state.running = False
                st.session_state.final_code = data.get("code", "# No code returned")

            st.session_state.last_status = qa_status

        if qa_status == "pending" and st.session_state.last_iterations >= 0:
            pass  # avoid spam; iteration change already added logs

    st.rerun()

# ── Final code output ──────────────────────────────────────────────────────────
if st.session_state.final_code:
    st.markdown('<hr class="neos-divider">', unsafe_allow_html=True)
    st.markdown("""
    <div class="code-panel-title">
      ✅ &nbsp; GENERATED ARTIFACT — READY FOR DEPLOYMENT
    </div>
    """, unsafe_allow_html=True)
    st.code(st.session_state.final_code, language="python")
    st.download_button(
        label="⬇️ Download Code",
        data=st.session_state.final_code,
        file_name=f"{st.session_state.thread_id or 'output'}.py",
        mime="text/plain",
    )
