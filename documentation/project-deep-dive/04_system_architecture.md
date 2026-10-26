# 04 — System Architecture Deep Dive

The **Kiro AI Assistant** follows a classic **client‑server** pattern with a thin web UI and a Python backend that handles conversation state, data access, and optional text‑to‑speech.

## High‑level components

```
[Browser UI] <--WebSocket/HTTP--> [Flask app]
    │                               │
    │                               ├─► **SocketIO** (real‑time channel)
    │                               ├─► **DialogueStateManager** (rule‑based intent & slot handling)
    │                               ├─► **HumanConversationManager** (orchestrates human‑in‑the‑loop flows)
    │                               ├─► **SessionManager** (JSON‑file persistence)
    │                               ├─► **Data Access Layer** (enhanced_data_access / order_data_access)
    │                               └─► **TTS Engine** (optional audio generation)
    │
    └─► HTTP routes for static pages, audio serving, health endpoint
```

### Layers & responsibilities
| Layer | What it does | Why it belongs here |
|------|--------------|---------------------|
| **Presentation** (templates + static) | Renders HTML UI, loads JavaScript that opens a Socket.IO connection. | Keeps UI separate from business logic; easy to replace with another front‑end framework. |
| **Transport** (Flask routes + Socket.IO) | Exposes HTTP endpoints (`/`, `/ecommerce`, `/audio/<id>`) and a bi‑directional `user_message` event. | Flask provides a simple WSGI server; Socket.IO adds real‑time capabilities needed for chat. |
| **Application / Service** | `app.py` wires together the managers; orchestrates request flow. | Centralises start‑up configuration (environment, TTS init, data loading). |
| **Conversation Management** | `DialogueStateManager`, `HumanConversationManager`, `ConversationState` objects. | Implements multi‑turn dialogue without external LLM; tracks intent, required slots, and completion. |
| **Persistence** | `SessionManager` (stores JSON files under `data/sessions`). | Allows sessions to survive process restarts; configurable storage type (JSON, memory). |
| **Data Access** | `data/enhanced_data_access.py` (reads JSON/CSV, aggregates customer stats) and fallback `order_data_access.py`. | Abstracts the source of order & customer data; enables richer analytics without the UI touching raw files. |
| **TTS Integration** | `tts_engine.py` (initialises a local TTS model, generates wav files asynchronously). | Optional voice feedback – encapsulated so the core dialogue does not depend on it. |
| **Testing** | `tests/` (pytest suites exercising each workflow). | Guarantees behaviour and serves as executable documentation. |

## Architectural patterns observed
* **Rule‑based Dialogue Engine** – deterministic intent detection via keyword tables, slot‑filling via explicit state machine.  This gives predictability and easy debugging, but limits natural‑language understanding.
* **Thin‑client / Server‑side Rendering** – Jinja templates render static pages; dynamic chat updates happen over Socket.IO, not via a SPA.  This reduces front‑end complexity.
* **Background Workers** – TTS initialisation and audio generation run in separate daemon threads; session cleanup runs in its own thread.  Simple threading is sufficient for a development prototype.
* **File‑based Persistence** – JSON files are used instead of a relational DB, which simplifies deployment but does not scale well for large user bases.
* **Separation of Concerns** – Business logic lives in `agents/`; data retrieval lives in `data/`; UI lives in `templates/`.

### What is *not* present
* No micro‑service decomposition – everything runs in a single Flask process.
* No event‑driven queue (e.g., RabbitMQ) – background tasks are simple threads.
* No external authentication/authorization layer.
* No containerisation or CI/CD pipeline in the repository.

---
*File saved as `docs/project-deep-dive/04_system_architecture.md`.*
