"""Token counting and history compaction for managing context size."""
from __future__ import annotations

import sys
import threading
from typing import List, Tuple

from nbchat.ui.chat_builder import build_messages
from nbchat.core.client import get_client


class CompactionEngine:
    """Compacts chat history when token count exceeds threshold."""

    def __init__(self, threshold: int, tail_messages: int = 5,
                 summary_prompt: str = None, summary_model: str = None,
                 system_prompt: str = ""):
        self.threshold = threshold
        self.tail_messages = tail_messages
        self.summary_prompt = summary_prompt or (
            "Summarize the conversation history above. Focus on:\n"
            "1. Key decisions made\n"
            "2. Important file paths and edits\n"
            "3. Tool calls and their outcomes (summarize large outputs)\n"
            "4. Next steps planned\n"
            "Keep it concise but preserve essential context."
        )
        self.summary_model = summary_model
        self.system_prompt = system_prompt
        self._cache: dict = {}
        self._cache_lock = threading.Lock()

    # ------------------------------------------------------------------
    # Token estimation
    # ------------------------------------------------------------------

    def _estimate_tokens(self, text: str) -> int:
        return max(1, len(text) // 3)

    def total_tokens(self, history: List[Tuple[str, str, str, str, str]]) -> int:
        """Estimate total tokens across all history entries.

        Counts content + tool_args for every row. For ``assistant_full``
        rows the payload is entirely in ``tool_args`` (a JSON blob); for
        ``analysis`` rows it is in ``content``. Both fields are always
        counted so no role is accidentally free.
        """
        total = 0
        for role, content, tool_id, tool_name, tool_args in history:
            msg_hash = hash((content, tool_args))
            with self._cache_lock:
                if msg_hash in self._cache:
                    total += self._cache[msg_hash]
                    continue

            tokens = self._estimate_tokens(content) + (
                self._estimate_tokens(tool_args) if tool_args else 0
            )
            with self._cache_lock:
                self._cache[msg_hash] = tokens
            total += tokens
        return total

    def should_compact(self, history: List[Tuple[str, str, str, str, str]]) -> bool:
        tokens = self.total_tokens(history)
        # Fire at 75% of threshold so compaction always has substantial
        # older content to summarise — avoids the tail consuming everything
        # by the time the hard limit is reached.
        trigger = int(self.threshold * 0.75)
        print(
            f"[compaction] token estimate: {tokens} / {self.threshold} (trigger={trigger})",
            file=sys.stderr,
        )
        return tokens >= trigger

    # ------------------------------------------------------------------
    # Compaction
    # ------------------------------------------------------------------

    def compact_history(
        self, history: List[Tuple[str, str, str, str, str]]
    ) -> List[Tuple[str, str, str, str, str]]:
        """Summarize the older portion of history, keeping the tail intact.

        Strategy
        --------
        1. Split history into ``older`` (to be summarised) and ``tail``
           (kept verbatim).
        2. ``tail_start`` is nudged backwards so it never lands in the
           middle of a logical turn (tool result / analysis / full-msg).
        3. Build API messages from ``older`` using the real system prompt
           so the model has full context, then append the summary request.
        4. Return ``[compacted_row] + tail``.
        """
        print(
            f"[compaction] compact_history called, history len={len(history)}, "
            f"tail_messages={self.tail_messages}",
            file=sys.stderr,
        )

        if len(history) <= self.tail_messages:
            print("[compaction] history too short to compact", file=sys.stderr)
            return history

        tail_start = len(history) - self.tail_messages

        # Walk backwards past incomplete turns so we don't split mid-exchange.
        # Clamp: never retreat more than tail_messages additional steps, so
        # ``older`` always retains substantial content to summarise.
        BOUNDARY_ROLES = {"tool", "analysis", "assistant_full"}
        max_retreat = self.tail_messages  # at most double the tail window
        steps = 0
        while (
            tail_start > 1
            and steps < max_retreat
            and history[tail_start][0] in BOUNDARY_ROLES
        ):
            tail_start -= 1
            steps += 1

        # If we still landed on a boundary role, just move forward until we
        # find a clean break rather than giving up entirely.
        while tail_start < len(history) - 1 and history[tail_start][0] in BOUNDARY_ROLES:
            tail_start += 1

        if tail_start <= 0:
            print("[compaction] could not find a clean boundary, skipping", file=sys.stderr)
            return history

        # Guard: if older is less than 20% of history, compacting is pointless.
        if tail_start < max(2, len(history) // 5):
            print(
                f"[compaction] older slice too small ({tail_start} rows), skipping",
                file=sys.stderr,
            )
            return history

        older = history[:tail_start]
        tail = history[tail_start:]

        print(
            f"[compaction] older={len(older)} rows, tail={len(tail)} rows",
            file=sys.stderr,
        )

        # Build messages from the older slice, using the real system prompt
        # so the summariser has full context.
        messages = build_messages(older, self.system_prompt)

        # Strip reasoning_content — it is an output-only field and will
        # cause errors or be silently dropped by most inference servers.
        for msg in messages:
            msg.pop("reasoning_content", None)

        # Append the summarisation instruction as a user turn.
        messages.append({"role": "user", "content": self.summary_prompt})

        print(
            f"[compaction] sending {len(messages)} messages to summariser",
            file=sys.stderr,
        )

        try:
            client = get_client()
            response = client.chat.completions.create(
                model=self.summary_model,
                messages=messages,
                max_tokens=4096,
            )
        except Exception as e:
            raise RuntimeError(f"Summarization failed: {e}") from e

        summary_text = response.choices[0].message.content
        print(
            f"[compaction] summary produced ({len(summary_text)} chars): "
            f"{summary_text[:120]}...",
            file=sys.stderr,
        )

        # Invalidate token cache — history shape has changed.
        with self._cache_lock:
            self._cache.clear()

        return [("compacted", summary_text, "", "", "")] + list(tail)


__all__ = ["CompactionEngine"]