# 01 — Executive Summary

## What the project does
The repository implements **Kiro AI Assistant**, a conversational customer‑care chatbot built with **Flask + Socket.IO**.  Users interact via a web UI (Jinja templates) that sends text messages over a WebSocket.  The backend:
1. Receives the message.
2. Passes it to a **DialogueStateManager** that orchestrates rule‑based multi‑turn conversations.
3. Looks up order information via an **enhanced data‑access layer** (JSON/CSV files).
4. Answers FAQ questions from a curated FAQ JSON dataset (and optionally from a support‑ticket dataset).
5. Optionally generates a voice response using a **TTS engine** (running asynchronously).
6. Persists the conversation state in a **SessionManager** (JSON files on disk by default).

## Problem it solves
* Provides a self‑service help‑desk for common e‑commerce/customer‑care queries (order status, billing, returns, product issues, etc.).
* Reduces human‑agent workload by handling routine questions automatically.
* Offers optional spoken responses for accessibility.

## Intended users
* End‑users of an e‑commerce or SaaS product needing quick support.
* Internally, support staff can view the same conversation history for hand‑off.

## Why the problem matters
Customer‑care volume is a major cost driver for online businesses.  An automated assistant improves response time, availability (24/7), and can scale without adding staff.

## Main features
| Feature | Description |
|---|---|
| **Web chat UI** | Flask‑served HTML with Socket.IO for real‑time messaging. |
| **Multi‑turn dialogue** | `DialogueStateManager` tracks conversation state, intents, and completion. |
| **Order lookup** | `data.enhanced_data_access.get_order_by_id` reads order data from JSON/CSV. |
| **FAQ answering** | Keyword‑based matching with domain‑aware filters; fallback to generic responses. |
| **Text‑to‑speech** | `tts_engine` loads a TTS model (e.g., edge‑tts) and streams audio files. |
| **Session persistence** | `SessionManager` stores sessions as JSON files (configurable storage type). |
| **Debug pages** | `/debug`, `/chat-debug` templates for developers. |

## Technology stack (detected from `requirements.txt` and imports)
* **Python 3.11+** (implicit from code style)
* **Flask 2.3.3** – web framework
* **Flask‑SocketIO 5.3.6** – real‑time bidirectional communication
* **python‑socketio 5.8.0** – client side for testing
* **pandas 2.3.3** – data loading / manipulation of JSON/CSV datasets
* **google‑generativeai 0.3.2** – imported but not used directly in the current code (available for future LLM calls).
* **TTS 0.22.0** – text‑to‑speech wrapper used by `tts_engine.py`.
* **python‑dotenv 1.0.0** – loads environment variables.
* **regex** – advanced regular‑expression handling.
* **openpyxl** – Excel support (used by some data scripts).

## Overall architecture (high‑level)
```
User ⇆ Browser (HTML/JS) ⇆ Flask (routes & SocketIO) ⇆ DialogueStateManager ⇆ Data Access Layer ⇆ FAQ / Order JSON files
                                          │
                                          └─► TTS Engine (optional audio generation)
```

## Current implementation status
* Core chat flow works – test suite passes for most paths.
* Enhanced data‑access layer is functional but falls back to legacy if dependencies missing.
* TTS integration is optional; it logs a warning when unavailable.
* No external database, auth, or deployment scripts are present yet.

## Strengths
* Clean separation: UI, dialogue manager, data access, and TTS are in distinct modules.
* Extensive pytest coverage for dialogue, FAQ, billing, and session handling.
* Asynchronous TTS generation keeps the UI responsive.

## Limitations / open gaps (to be addressed in later phases)
* **No persistent DB** – scalability limited to file‑based storage.
* **Authentication absent** – anyone can hit the endpoint.
* **LLM integration stubbed** – `google‑generativeai` is imported but not used; the system is currently rule‑based.
* **Deployment** – only `socketio.run(app, debug=True)`; no Docker/CI/CD.
* **Frontend** – static Jinja templates; no SPA or progressive enhancement.
* **Error handling** – many `print` statements; no structured logging or monitoring.

---
*This executive summary will be the first page of the documentation suite (`docs/project-deep-dive/01_executive_summary.md`).*
