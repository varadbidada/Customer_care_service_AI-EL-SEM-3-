# 03 — Technology Stack: WHAT, WHY, AND ALTERNATIVES

| Technology | Actual Usage in Codebase | Why It Fits | Alternatives | Trade‑offs |
|------------|--------------------------|------------|--------------|-----------|
| **Python 3.11+** | Core language for all modules (`app.py`, `agents/`, `data/`, tests). | Modern syntax, strong ecosystem, easy rapid development. | Python 3.9/3.10 (older) or other languages (Node.js, Go). | Newer versions have better performance and typing support; older versions may lack some std‑lib features used (e.g., `dataclasses` enhancements). |
| **Flask 2.3.3** | Web framework (`Flask(__name__)`, route definitions, `render_template`). | Lightweight, easy to integrate with Socket.IO, good for prototyping. | Django (full‑stack), FastAPI (async‑first). | Flask is synchronous by default; FastAPI would allow async endpoints and better concurrency. |
| **Flask‑SocketIO 5.3.6** | Real‑time bi‑directional communication (`socketio.on('user_message')`). | Simple integration with Flask, works over WebSockets or long‑polling. | plain `socket.io` client + custom server, FastAPI with `websockets`. | Adds a dependency and some overhead; pure async solutions may be more scalable. |
| **python‑socketio 5.8.0** | Used in tests to simulate client‑side Socket.IO interactions. | Mirrors server library, enables unit tests without browser. | None needed if only server‑side tests. | Extra package size, but useful for test isolation. |
| **pandas 2.3.3** | Loads FAQ JSON into `DataFrame` (`pd.DataFrame(faq_data)`), manipulates order tables. | Powerful data handling, filtering, and aggregation for FAQ lookup and stats. | csv/json built‑in modules, `polars` (faster). | Pandas is heavy memory‑wise; for simple lookups a dict/list could be lighter. |
| **google‑generativeai 0.3.2** | Imported in `agents/llm_service.py` but not invoked yet. | Provides a hook for future LLM integration (Gemini models). | OpenAI SDK, Anthropic SDK. | Currently unused – extra dependency without runtime impact. |
| **python‑dotenv 1.0.0** | Loads environment variables from `.env` (`load_dotenv()`). | Keeps secrets/config separate from code. | Pass env vars directly, config files (YAML). | Slight overhead; works well for local development. |
| **TTS 0.22.0** | Text‑to‑speech wrapper (`tts_engine.initialize_tts()`, `speak_async`). | Enables optional voice responses for accessibility. | pyttsx3, gTTS, external services (Amazon Polly). | Local TTS may be slower, limited voice options; cloud services offer higher quality but cost. |
| **regex 2023.10.3** | Advanced regex handling in `agents/` for order/customer ID extraction. | More features than Python `re` (e.g., fuzzy matching). | Built‑in `re`. | Adds dependency; for simple patterns built‑in `re` suffices. |
| **openpyxl 3.1.2** | Used by some data scripts to read/write Excel files (e.g., `extract_test_data.py`). | Handles Excel datasets without needing Excel installed. | pandas `read_excel` (which itself uses `openpyxl`). | Only needed if Excel files are actually used; otherwise extra weight. |

### Deep‑dive for each technology

1. **Python** – The entire project is written in Python, leveraging its readability and rapid prototyping. The code uses type hints, `dataclasses`, and modern f‑strings. If the team prefers static typing, `mypy` could be added.
2. **Flask** – Chosen for its minimal footprint; the app only serves a few HTML pages and a Socket.IO endpoint. It runs synchronously, which is sufficient for the current load (single‑process dev server). For high‑traffic production, an async framework (FastAPI) or a WSGI server like Gunicorn with multiple workers would be needed.
3. **Flask‑SocketIO** – Provides the real‑time chat channel required for the assistant. It abstracts WebSocket handling and falls back to long‑polling, ensuring compatibility with browsers that may block websockets.
4. **pandas** – Used to load the FAQ JSON into a `DataFrame` for fast filtering by domain and keyword matching. This gives O(n) operations for lookups, which is acceptable for a few thousand FAQs. If the FAQ set grew to >100k entries, a dedicated search index (e.g., Elasticsearch) would be more efficient.
5. **google‑generativeai** – Present as a placeholder for future LLM calls. The current design is rule‑based, but the stub shows the intention to switch to an LLM‑driven dialogue later.
6. **TTS** – Provides optional audio responses. The engine is initialised in a background thread to avoid blocking startup. Audio files are cached in `static/audio/` and served via `/audio/<id>`.
7. **regex** – Enables more flexible pattern extraction (e.g., extracting numeric order IDs from arbitrary user text). The standard library could replace it, but `regex` offers better Unicode handling.
8. **openpyxl** – Used by utility scripts for Excel data conversion; not part of the production path.

---
*Saved as `docs/project-deep-dive/03_technology_stack.md`.*
