# Supervisor Feature Design Document

This document captures the technical design for the **Supervisor** feature that will sit between the chat UI and the `llama-server` binary. It is intended as a reference for the implementation phase.

---

## 1.  Purpose
The Supervisor provides a per‑session monitoring layer that:

1. **Observes** the assistant’s token stream in real time.
2. **Analyzes** each token against policy rules or a machine‑learning model.
3. **Intervenes** by pausing the current generation, injecting corrective text, and resuming the original stream.

The goal is to keep conversations on track without compromising latency or requiring changes to the existing `llama-server` binary.

---

## 2.  Existing Infrastructure Overview

| Component | Role | Current Interaction | Notes |
|-----------|------|---------------------|-------|
| `nbchat/core/client.py` | OpenAI client | Calls `SERVER_URL/v1` | Hard‑coded API key, no streaming hooks |
| `nbchat/core/config.py` | Config constants | Provides `SERVER_URL` (default `http://localhost:8000`) | Static |
| `run.py` | Service starter | Boots `llama-server` | No monitoring or supervisor |
| Streamlit UI | Front‑end | Calls `/v1/chat/completions` with `stream=True` | Receives SSE tokens |

The only place tokens are produced is the SSE stream from `llama-server`.

---

## 3.  High‑Level Architecture

```
+----------------+          +----------------+          +----------------+
|  Streamlit UI  |  <-----> |  Chat API (FastAPI)   |  llama‑server |
|  (frontend)    |  SSE  -> |  (OpenAI API wrapper) |  (C++ binary) |
+----------------+          +----------------+          +----------------+
          ^                          ^
          |                          |
          |      +----------------+   |
          |      |  Supervisor    |   |
          +------|  (Python)      |---+
                 +----------------+
```

* The **Chat API** forwards user requests to `llama-server` and streams the response to the UI.
* The **Supervisor** consumes the same token stream, performs checks, and can interrupt the stream by sending a new request with corrective text.

---

## 4.  Core Interaction Flow

1. **Session Start** ➜ backend creates a `Supervisor(session_id, SERVER_URL)` and calls `await supervisor.start()`.

2. **Token Streaming** ➜ UI calls `/v1/chat/completions` (`stream=True`). The Chat API launches an async generator that yields tokens from `llama-server`. Two copies of the generator are used:
   * One feeds the UI.
   * Another pushes tokens into `Supervisor._token_queue`.

3. **Supervisor Analysis** ➜ The supervisor consumes tokens from the queue, running `analyze_token(token)` after each token. If a violation is detected, `interject(guidance)` is invoked.

4. **Interjection** ➜ `interject` cancels the current SSE stream, posts a new assistant message containing the guidance, and then resumes the original stream.

5. **Session End** ➜ Backend calls `await supervisor.stop()` to clean up.

---

## 5.  Component Design

### Supervisor
```python
class Supervisor:
    def __init__(self, session_id: str, chat_api_url: str):
        self._token_queue: asyncio.Queue[str] = asyncio.Queue()
        self._stop_event = asyncio.Event()
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        self._task = asyncio.create_task(self._run())

    async def stop(self):
        self._stop_event.set()
        if self._task:
            await self._task

    async def _run(self):
        while not self._stop_event.is_set():
            token = await self._token_queue.get()
            await self.analyze_token(token)

    async def analyze_token(self, token: str):
        # Replace with real policy logic
        if token.lower() in {"badword"}:
            await self.interject("I\'m sorry, but I can\'t continue with that.")

    async def interject(self, guidance: str):
        # Cancel the current stream
        self._stop_event.set()
        # Send the guidance as a new assistant message
        await send_message(self.chat_api_url, self.session_id,
                           role="assistant", content=guidance)
        # Clear the event to resume
        self._stop_event.clear()
```

### Token Queue & Abortable Generator
The Chat API should expose a generator that accepts an `asyncio.Event` to abort the stream. When `interject()` sets the event, the generator raises `asyncio.CancelledError`, which the UI can catch and ignore.

### Policy Engine
Currently a simple rule‑based check (`is_disallowed(token)`). The design allows swapping this with an ML model or external policy service.

---

## 6.  High‑Level Implementation Plan

| Step | Description | Deliverable |
|------|-------------|-------------|
| 1 | Define token‑queue contract and abortable generator API | Spec docs |
| 2 | Extend `nbchat/core/client.py` to push tokens into the queue | Updated client |
| 3 | Implement `Supervisor` class (basic lifecycle + token consumption) | `nbchat/supervisor.py` |
| 4 | Add abortable streaming generator to Chat API | SSE wrapper |
| 5 | Implement `interject` logic (POST new message, resume stream) | Full flow |
| 6 | Replace stub policy with real rules or ML model | Policy module |
| 7 | Update Streamlit UI to handle interjected messages | UI changes |
| 8 | Add session‑level hooks to create/destroy supervisor | Hook integration |
| 9 | Write unit & integration tests | Test suite |
|10 | Produce documentation & diagrams | Updated README & this file |

---

## 7.  Risks & Mitigations

| Risk | Mitigation |
|------|-------------|
| **Latency spikes** when interjecting | Keep interjection brief; reuse the same HTTP connection if possible |
| **Token loss** during pause | Buffer tokens in the queue; resume from last token |
| **Concurrent chats** | Store supervisors in a thread‑safe dict keyed by session ID |
| **API key leakage** | Remove hard‑coded key; use environment variables |

---

## 8.  Next Steps
1. Create a minimal prototype of the supervisor.
2. Verify that the UI continues to stream tokens while the supervisor is active.
3. Iterate on policy logic and interjection handling.
4. Refactor for production‑grade logging, error handling, and configuration.

---

*This document is a living artifact and should be updated as the feature progresses.*
