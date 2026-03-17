<div align="center">

# 🤖 Autonomous Multi-Agent Dev Squad

**A production-grade Proof of Concept for self-correcting, agentic software engineering.**

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1.x-FF6B35?style=for-the-badge&logo=langchain&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.55-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-Google_AI-4285F4?style=for-the-badge&logo=google&logoColor=white)

</div>

---

## 📌 Overview

This project is a **Proof of Concept** demonstrating how a team of specialized AI agents can autonomously handle a software engineering task end-to-end — from understanding a feature request to writing, testing, and fixing code — **without human intervention**.

The system uses a **LangGraph state machine** to orchestrate a squad of agents that communicate through a shared memory state. The critical innovation is the **self-correction loop**: if the generated code fails QA, the system automatically retries with real error feedback, just like a real developer would.

> Built as a portfolio project targeting a Lead AI/MLOps Engineer role, demonstrating deep understanding of agentic architectures, LLM orchestration, and cloud-native deployment patterns.

---
<img src="https://github.com/MinhHieu13-cmc/Multi-Agent_Dev_Squad/blob/main/image/Real-time%20self-correction%20loop%20in%20action.png" alt="Demo" width="100%">

## 🏗️ Architecture: The Self-Correction Loop

```
  ┌─────────────────────────────────────────────────────────────────┐
  │                    LangGraph State Machine                       │
  │                                                                  │
  │   User Prompt                                                    │
  │       │                                                          │
  │       ▼                                                          │
  │  ┌─────────┐      Plan       ┌─────────┐      Code              │
  │  │  LEAD   │ ─────────────► │  CODER  │ ─────────────────┐     │
  │  │ (Plan)  │                 │ (Write) │                  │     │
  │  └─────────┘                 └─────────┘                  ▼     │
  │                                  ▲              ┌──────────────┐│
  │                                  │   FAILED     │  QA AGENT   ││
  │                          Error   │◄─────────────│  (Docker    ││
  │                          Logs    │              │   Sandbox)  ││
  │                                  │   PASSED     └──────────────┘│
  │                                  │                  │           │
  │                                  └──────────────    ▼           │
  │                                              ┌─────────┐        │
  │                                              │  SAVER  │        │
  │                                              │(outputs/)│       │
  │                                              └─────────┘        │
  └─────────────────────────────────────────────────────────────────┘
```

### The Four Agents

| Agent | Role | Key Capability |
|---|---|---|
| **🧠 Lead** | Planner & Orchestrator | Decomposes any feature request into a structured engineering plan |
| **💻 Coder** | Implementer | Writes code from the plan; rewrites it from error logs on failure |
| **🧪 QA Agent** | Verifier | Provisions an **ephemeral Docker container** and executes the code in isolation |
| **💾 Saver** | Artifact Manager | Persists verified code to `outputs/<thread_id>.py` |

### ⚡ Technical Highlight: Docker-in-Docker Sandboxing

The QA Agent achieves **true code isolation** by spinning up sibling Docker containers from *inside* the backend container. This is enabled by mounting the host Docker socket:

```yaml
# docker-compose.yml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
```

This is a production-level pattern used in CI/CD systems (e.g., GitHub Actions runners, Jenkins agents). The generated code runs inside a `python:3.10-slim` container with:
- ✅ Memory limited to `128m`
- ✅ Network access disabled
- ✅ Container auto-removed after execution
- ✅ 10-second execution timeout

If the code crashes, the real stderr output is captured and fed directly back to the Coder LLM as context for the next fix attempt.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Agent Orchestration** | [LangGraph](https://langchain-ai.github.io/langgraph/) | State machine for multi-agent workflows |
| **LLM** | Gemini 2.5 Flash (Google AI) | Reasoning engine for Lead and Coder agents |
| **API Backend** | FastAPI + Uvicorn | Async task submission and status polling |
| **State Persistence** | SQLite + LangGraph Checkpointer | Survive restarts, resume interrupted tasks |
| **Code Sandbox** | Docker (DinD via socket mount) | Secure, isolated code execution environment |
| **Frontend** | Streamlit | Real-time Mission Control dashboard |
| **Deployment** | Docker Compose | One-command production stack |
| **Live Tunneling** | ngrok | Expose local demo to the internet instantly |

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Notes |
|---|---|
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | Must be **running** — needed for sandboxed code execution |
| [Google Gemini API Key](https://aistudio.google.com/apikey) | Free tier is sufficient for demos |

### 1. Clone

```bash
git clone https://github.com/MinhHieu13-cmc/Multi-Agent_Dev_Squad.git
cd Multi-Agent_Dev_Squad
```

### 2. Configure Environment

```bash
cp .env.example .env
# Open .env and add your key:
# GOOGLE_API_KEY=
```

### 3. Launch the Stack

```bash
docker-compose up -d --build
```

This single command:
- Builds a shared image with Python 3.11, all dependencies, and the Docker CLI
- Starts the **FastAPI backend** on port `8000` with the Docker socket mounted
- Starts the **Streamlit frontend** on port `8501`, pre-wired to the backend
- Both services restart automatically if they crash (`restart: unless-stopped`)

### 4. Open Mission Control

```
http://localhost:8501
```

Type any feature request (e.g., *"Write a secure bcrypt password hashing function in Python"*) and click **Deploy Squad**. Watch the agents think, write, fail, and fix — live.

---

## 🌐 Live Demo via ngrok

To share a public URL with anyone (recruiters, interviewers):

```bash
# Install ngrok and authenticate once
ngrok config add-authtoken <YOUR_TOKEN>

# Expose the Streamlit UI
ngrok http 8501
```

Share the `https://xxxx.ngrok-free.app` URL. The backend remains private — only the UI is exposed.

> **Windows users:** Use `.\start_demo.ps1` to launch the full stack + ngrok in one command.

---

## 📁 Project Structure

```
Multi-Agent_Dev_Squad/
├── app/
│   ├── nodes/
│   │   ├── lead.py       # Lead Agent — planning with Gemini
│   │   ├── coder.py      # Coder Agent — code generation with Gemini
│   │   ├── qa.py         # QA Agent — Docker sandbox execution
│   │   └── saver.py      # Saver Agent — artifact persistence
│   ├── tools/
│   │   └── sandbox.py    # Docker-in-Docker sandbox utility
│   ├── graph.py          # LangGraph StateGraph definition
│   └── state.py          # AgentState TypedDict (shared memory)
├── worker.py             # FastAPI application (task submission & polling)
├── app_ui.py             # Streamlit Mission Control dashboard
├── Dockerfile            # Single image for both backend and frontend
├── docker-compose.yml    # Two-service production stack
├── start_demo.ps1        # Windows one-command demo launcher + ngrok
├── start_demo.sh         # Linux/macOS one-command demo launcher + ngrok
├── .env.example          # Template for required environment variables
└── outputs/              # Generated code artifacts (git-ignored)
```

---

## 📊 How It Works — Step by Step

1. **User submits a prompt** via the Streamlit UI or `POST /task` API.
2. **FastAPI** creates a background task and returns a `thread_id` immediately.
3. **LangGraph** starts the state machine:
   - The **Lead Agent** calls Gemini 2.5 Flash to produce a structured plan.
   - The **Coder Agent** calls Gemini 2.5 Flash to write the implementation.
   - The **QA Agent** writes the code to a temp file, mounts it into a fresh `python:3.10-slim` container, runs it, and captures stdout/stderr.
4. **If the code fails:** error logs are injected into the Coder's context and the loop repeats (up to a configurable max iterations).
5. **If the code passes:** the Saver Agent writes `outputs/<thread_id>.py` to disk.
6. **The Streamlit UI polls** `GET /task/{thread_id}` every 1.5 seconds and renders the live agent activity log, making the self-correction loop fully visible.

---

## 🔧 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/task` | `POST` | Submit a new task. Body: `{"prompt": "...", "thread_id": "optional"}` |
| `/task/{thread_id}` | `GET` | Poll task status, code, and execution logs |
| `/docs` | `GET` | Interactive Swagger UI |

---

<div align="center">

Built with ❤️ as a portfolio demonstration of agentic AI systems.

</div>
