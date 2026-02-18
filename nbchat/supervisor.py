"""nbchat.supervisor
=====================

This module contains the design ideas for a *supervisor* component that can
interact with a running :mod:`llama-server` instance while a user is having a
conversation with the assistant.  The supervisor is **not** a production
implementation – it is a detailed blueprint that can be turned into working code
once the surrounding application has been extended to expose the necessary
hooks.

Key requirements
-----------------
1. **Per‑session supervisor** – a dedicated supervisor instance is created
   when a chat session starts and is terminated when the session ends.
2. **Continuous monitoring** – while the assistant is generating a response,
   the supervisor examines the token stream in real time to ensure the
   assistant stays on track and does not produce policy violations or
   factual errors.
3. **Real‑time interjection** – the supervisor must be able to pause the
   assistant at any point, inject guidance or corrective text, and then let the
   assistant continue.

Assumptions
-----------
* The chat application uses the OpenAI compatible endpoint exposed by
  :mod:`llama-server` (see :file:`nbchat/core/config.py`).
* Streaming responses are delivered via **Server‑Sent Events** (SSE), which
  provide a token‑by‑token callback.
* The application already keeps a per‑session conversation history in memory
  (or a lightweight database).  The supervisor can read from this store.
* We are free to add new routes or middleware to the FastAPI/Flask stack that
  serves the chat UI.

High‑level architecture
-----------------------
```
Client <---> Chat API (FastAPI) <---> llama‑server
                  ^
                  |  (streaming SSE)
                  v
            Supervisor Service
```

* The chat API forwards user messages to :mod:`llama-server` and streams
  tokens back to the client.
* A background task, **Supervisor**, is started for each session.  It listens
  to the same SSE stream that the client receives – it can either wrap the
  original generator or subscribe to a shared asyncio queue.
* When the supervisor decides that an interjection is required, it **cancels**
  the current SSE connection (by closing the iterator) and sends a new request
  to the server with a *system* or *assistant* message containing the
  corrective guidance.  After the interjection completes, the original
  stream is resumed.

Implementation outline
----------------------
The following pseudo‑code demonstrates the core idea.  It is intentionally
light‑weight and can be expanded with error handling, policy checks, or
machine‑learning models.

```python
class Supervisor:
    def __init__(self, session_id: str, chat_api_url: str):
        self.session_id = session_id
        self.chat_api_url = chat_api_url
        self._running = asyncio.Event()
        self._stop = asyncio.Event()
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the supervisor background task."""
        self._running.set()
        self._task = asyncio.create_task(self._run())

    async def stop(self):
        """Signal the supervisor to terminate and wait for cleanup."""
        self._stop.set()
        if self._task:
            await self._task

    async def _run(self):
        """Main loop that consumes the assistant token stream.

        The loop fetches tokens from the streaming endpoint via an async
        generator.  After each token, :func:`analyze_token` is called to
        decide whether an interjection is needed.
        """
        async for token in stream_assistant(self.session_id):
            if self._stop.is_set():
                break
            await self.analyze_token(token)
            yield token

    async def analyze_token(self, token: str):
        """Apply simple heuristics or policy models.

        If the token triggers a violation (e.g. a disallowed word), the
        supervisor calls :func:`interject`.
        """
        if is_disallowed(token):
            await self.interject("I’m sorry, but I can’t continue with that.")

    async def interject(self, guidance: str):
        """Pause the current stream and inject a new assistant message.

        Implementation steps:
        1. Close the current SSE iterator.
        2. Send a new request to :mod:`llama-server` with the guidance as an
           assistant message.
        3. Stream the response back to the client.
        4. Resume the original stream.
        """
        # Pseudo‑code – the actual implementation will need to coordinate
        # with the FastAPI streaming endpoint.
        pass
```

Key design decisions
---------------------
* **Separation of concerns** – The supervisor is a distinct component that
  does not modify the chat API or the llama‑server binary.  It interacts only
  through the public HTTP API.
* **Non‑blocking interjection** – By cancelling the SSE connection, the
  supervisor can interrupt the assistant instantly.  The FastAPI endpoint
  must expose a way to abort the generator, which can be achieved by using
  ``asyncio.CancelledError`` or a shared ``asyncio.Event``.
* **Thread‑safe token queue** – If the chat API already streams tokens to a
  client, we can pipe those tokens into an ``asyncio.Queue`` that the
  supervisor consumes.  This avoids duplicating network traffic.
* **Policy engine** – The ``analyze_token`` method can be a simple rule‑based
  check or a more sophisticated ML model that runs locally.  The design
  leaves room for future extension.

Integration steps (to be implemented elsewhere)
----------------------------------------------
1. **Hook into chat session creation** – When a new chat is started, the
   application creates a :class:`Supervisor` instance and calls
   ``await supervisor.start()``.  The supervisor is stored in a session‑level
   dictionary.
2. **Wrap the SSE generator** – The FastAPI endpoint that streams the
   assistant response should forward tokens to both the client and the
   supervisor queue.  The supervisor then yields tokens back to the client
   (possibly after interjection).
3. **Graceful shutdown** – When the session ends, the application calls
   ``await supervisor.stop()`` to clean up.

Testing strategy
-----------------
* Unit tests for the :class:`Supervisor` class can inject a mock streaming
  generator and verify that ``interject`` is called under the right
  conditions.
* Integration tests can spin up a real :mod:`llama-server` instance, start a
  chat session, and confirm that the supervisor can pause and resume the
  assistant.

Future work
-----------
* Persist supervisor state across restarts.
* Add configuration for custom policy rules.
* Support multiple assistants or multi‑turn conversations.
* Benchmark the impact on latency.

End of design document.
"""

from __future__ import annotations

import asyncio
from typing import AsyncGenerator, Optional

# The following imports are placeholders – the real implementation will
# depend on the chat API and the HTTP client library used by the project.
# from nbchat.chat_api import stream_assistant, send_message


class Supervisor:
    """Supervisor for a single chat session.

    Parameters
    ----------
    session_id:
        Unique identifier for the chat session.
    chat_api_url:
        Base URL of the OpenAI‑compatible endpoint (e.g. ``http://localhost:8000``).
    """

    def __init__(self, session_id: str, chat_api_url: str):
        self.session_id = session_id
        self.chat_api_url = chat_api_url
        self._running = asyncio.Event()
        self._stop = asyncio.Event()
        self._task: Optional[asyncio.Task] = None
        # An asyncio.Queue that receives tokens from the chat API.
        self._token_queue: asyncio.Queue[str] = asyncio.Queue()

    # ---------------------------------------------------------------------
    # Lifecycle helpers
    # ---------------------------------------------------------------------
    async def start(self) -> None:
        """Start the supervisor background task."""
        self._running.set()
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        """Signal the supervisor to terminate and wait for cleanup."""
        self._stop.set()
        if self._task:
            await self._task

    # ---------------------------------------------------------------------
    # Core logic
    # ---------------------------------------------------------------------
    async def _run(self) -> None:
        """Consume assistant tokens from the queue.

        The chat API is expected to push tokens into ``self._token_queue`` as
        they are streamed from :mod:`llama-server`.  The supervisor processes
        each token, performs analysis, and optionally interjects.
        """
        while not self._stop.is_set():
            try:
                token = await asyncio.wait_for(self._token_queue.get(), timeout=5.0)
            except asyncio.TimeoutError:
                continue  # No token received – loop again.
            await self.analyze_token(token)
            # In a real implementation this would yield the token to the
            # client via the streaming endpoint.

    async def analyze_token(self, token: str) -> None:
        """Apply policy checks to a single token.

        This example simply blocks on a hard‑coded disallowed word.  Replace
        with a more sophisticated rule set or ML model.
        """
        if token.lower() in {"badword", "anotherbadword"}:
            await self.interject(
                "I’m sorry, but I can’t continue with that."
            )

    async def interject(self, guidance: str) -> None:
        """Pause the current assistant stream and inject a corrective message.

        The supervisor accomplishes this by:
        1. Cancelling the current stream (implementation‑dependent).
        2. Sending a new assistant message containing *guidance*.
        3. Resuming the original stream.
        """
        # Cancel the current stream – the FastAPI endpoint must support
        # cancellation via an asyncio.Event or similar.
        self._stop.set()
        # Send the guidance as an assistant message.
        await send_message(self.chat_api_url, self.session_id, role="assistant", content=guidance)
        # Restart the stream.
        self._stop.clear()
        # In a real system we would re‑initiate the SSE stream and feed
        # tokens back into ``self._token_queue``.


# -------------------------------------------------------------------------
# Helper functions – placeholders for the real implementations
# -------------------------------------------------------------------------
async def send_message(api_url: str, session_id: str, *, role: str, content: str) -> None:
    """Send a single message to the chat API.

    This is a stub – the actual implementation would POST to
    ``{api_url}/v1/chat/completions`` with the appropriate JSON payload
    and ``stream: true`` flag.
    """
    pass
