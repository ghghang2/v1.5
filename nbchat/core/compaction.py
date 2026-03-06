"""Compaction Engine — keeps context within token limits by summarising history."""
from __future__ import annotations

import logging
import threading
from typing import List, Tuple, Optional

from nbchat.ui.chat_builder import build_messages
from .client import get_client

_log = logging.getLogger("nbchat.compaction")
if not _log.handlers:
    _h = logging.FileHandler("compaction.log", mode="a")
    _h.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    _log.addHandler(_h)
    _log.setLevel(logging.DEBUG)

_Row = Tuple[str, str, str, str, str]
_DEPENDENT_ROLES = {"tool", "analysis", "assistant_full"}


class CompactionEngine:

    def __init__(self, threshold, tail_messages=5, summary_prompt="",
                 summary_model="", system_prompt=""):
        self.threshold = threshold
        self.tail_messages = tail_messages
        self.summary_prompt = summary_prompt
        self.summary_model = summary_model
        self.system_prompt = system_prompt
        self.context_summary: str = ""
        self._cache: dict = {}
        self._cache_lock = threading.Lock()

    # ------------------------------------------------------------------
    # Token estimation
    # ------------------------------------------------------------------

    def _estimate_tokens(self, text: str) -> int:
        return max(1, len(text) // 3)

    def total_tokens(self, history: List[_Row]) -> int:
        total = 0
        for role, content, tool_id, tool_name, tool_args in history:
            key = hash((content, tool_args))
            with self._cache_lock:
                cached = self._cache.get(key)
            if cached is not None:
                total += cached
                continue
            tokens = self._estimate_tokens(content) + (
                self._estimate_tokens(tool_args) if tool_args else 0
            )
            with self._cache_lock:
                self._cache[key] = tokens
            total += tokens
        return total

    def should_compact(self, history: List[_Row]) -> bool:
        history_tokens = self.total_tokens(history)
        # Count the context_summary too — it is injected into the system prompt
        # and consumes real context window space on every API call.
        summary_tokens = (
            self._estimate_tokens(self.context_summary)
            if self.context_summary else 0
        )
        tokens = history_tokens + summary_tokens
        trigger = int(self.threshold * 0.75)
        _log.debug(
            f"token estimate: {tokens} "
            f"(history={history_tokens}, summary={summary_tokens}) "
            f"/ {self.threshold} (trigger={trigger})"
        )
        return tokens >= trigger

    # ------------------------------------------------------------------
    # Turn grouping
    # ------------------------------------------------------------------

    @staticmethod
    def _group_into_turns(history: List[_Row]) -> List[List[_Row]]:
        turns: List[List[_Row]] = []
        current: List[_Row] = []
        for row in history:
            if row[0] == "user" and current:
                turns.append(current)
                current = []
            current.append(row)
        if current:
            turns.append(current)
        return turns

    # ------------------------------------------------------------------
    # Safe tail — never returns empty
    # ------------------------------------------------------------------

    @staticmethod
    def _safe_tail(history: List[_Row], n: int) -> List[_Row]:
        """Return last n rows starting at a structurally safe boundary.

        Falls back progressively:
        1. Walk forward past dependent roles from tail_start.
        2. Walk backward to nearest user row.
        3. Return full history rather than empty list.
        """
        if not history or n <= 0:
            return history

        tail_start = max(0, len(history) - n)

        probe = tail_start
        while probe < len(history) and history[probe][0] in _DEPENDENT_ROLES:
            probe += 1
        if probe < len(history):
            return history[probe:]

        probe = len(history) - 1
        while probe > 0 and history[probe][0] != "user":
            probe -= 1
        if history[probe][0] == "user":
            _log.debug(f"_safe_tail: fell back to user boundary at index {probe}")
            return history[probe:]

        _log.debug("_safe_tail: no user boundary found, returning full history")
        return history

    # ------------------------------------------------------------------
    # Tool result truncation
    # ------------------------------------------------------------------

    @staticmethod
    def _truncate_tool_results(rows: List[_Row], budget: int) -> List[_Row]:
        """Truncate oversized tool results largest-first until rows fit budget."""
        def est(text: str) -> int:
            return max(1, len(text) // 3)

        result = list(rows)
        total = sum(est(r[1]) + (est(r[4]) if r[4] else 0) for r in result)

        if total <= budget:
            return result

        tool_indices = sorted(
            [i for i, r in enumerate(result) if r[0] == "tool"],
            key=lambda i: len(result[i][1]),
            reverse=True,
        )

        for idx in tool_indices:
            if total <= budget:
                break
            role, content, tid, tname, targs = result[idx]
            excess_chars = (total - budget) * 3
            keep = max(200, len(content) - excess_chars)
            notice = (
                f"\n[...output truncated from {len(content)} to {keep} chars"
                f" to fit context window...]"
            )
            new_content = content[:keep] + notice
            saved = est(content) - est(new_content)
            result[idx] = (role, new_content, tid, tname, targs)
            total -= saved
            _log.debug(
                f"truncated tool result '{tname}' "
                f"{len(content)} -> {len(new_content)} chars"
            )

        return result

    # ------------------------------------------------------------------
    # Intra-turn safe split
    # ------------------------------------------------------------------

    @staticmethod
    def _find_safe_split(group: List[_Row]) -> Optional[int]:
        for i in range(1, len(group)):
            role = group[i][0]
            prev_role = group[i - 1][0]
            if role not in _DEPENDENT_ROLES and prev_role != "assistant_full":
                return i
        return None

    # ------------------------------------------------------------------
    # Core compaction
    # ------------------------------------------------------------------

    def compact_history(self, history: List[_Row]) -> List[_Row]:
        _log.debug(
            f"compact_history called, history len={len(history)}, "
            f"tail_messages={self.tail_messages}"
        )

        if len(history) <= self.tail_messages:
            _log.debug("history too short to compact")
            return history

        turns = self._group_into_turns(history)

        # Reserve space for context_summary (existing + new one being produced).
        # Target: tail rows use at most 50% of threshold so summary fits too.
        summary_tokens = (
            self._estimate_tokens(self.context_summary)
            if self.context_summary else 0
        )
        tail_budget = max(
            int(self.threshold * 0.40),
            int(self.threshold * 0.75) - summary_tokens,
        )
        _log.debug(
            f"tail_budget={tail_budget} tokens "
            f"(summary_tokens={summary_tokens}, threshold={self.threshold})"
        )

        to_summarise: List[_Row] = []
        remaining_turns: List[List[_Row]] = list(turns)

        while remaining_turns:
            remaining_flat = [row for t in remaining_turns for row in t]
            if self.total_tokens(remaining_flat) <= tail_budget:
                break

            candidate_turn = remaining_turns[0]
            after_drop = [row for t in remaining_turns[1:] for row in t]

            if not after_drop:
                # Last remaining turn.
                split_idx = self._find_safe_split(candidate_turn)
                if split_idx is not None:
                    to_summarise.extend(candidate_turn[:split_idx])
                    remaining_turns[0] = candidate_turn[split_idx:]
                    _log.debug(
                        f"intra-turn split at index {split_idx} "
                        f"within last turn of {len(candidate_turn)} rows"
                    )
                else:
                    _log.debug(
                        "cannot split last remaining turn — "
                        "truncating oversized tool results in place"
                    )
                    truncated = self._truncate_tool_results(candidate_turn, tail_budget)
                    self.context_summary = self._call_summariser(
                        to_summarise if to_summarise else history
                    )
                    with self._cache_lock:
                        self._cache.clear()
                    return truncated
                break

            turn_tokens = self.total_tokens(candidate_turn)
            if turn_tokens >= tail_budget:
                split_idx = self._find_safe_split(candidate_turn)
                if split_idx is not None:
                    to_summarise.extend(candidate_turn[:split_idx])
                    remaining_turns[0] = candidate_turn[split_idx:]
                    _log.debug(
                        f"oversized turn ({turn_tokens} tokens): "
                        f"intra-turn split at index {split_idx}"
                    )
                    continue
                _log.debug(
                    f"oversized turn with no safe split "
                    f"({turn_tokens} tokens) — truncating tool results"
                )
                remaining_turns[0] = self._truncate_tool_results(
                    candidate_turn, tail_budget
                )
                to_summarise.extend(remaining_turns.pop(0))
                continue

            to_summarise.extend(remaining_turns.pop(0))

        if not to_summarise:
            _log.debug("nothing to summarise")
            return history

        remaining_history = [row for t in remaining_turns for row in t]

        if not remaining_history:
            _log.debug(
                "remaining_history empty after loop — falling back to safe tail"
            )
            remaining_history = self._safe_tail(history, self.tail_messages)

        _log.debug(
            f"summarising {len(to_summarise)} rows, "
            f"keeping {len(remaining_history)} rows"
        )

        self.context_summary = self._call_summariser(to_summarise)

        with self._cache_lock:
            self._cache.clear()

        return remaining_history

    # ------------------------------------------------------------------
    # Summariser call
    # ------------------------------------------------------------------

    def _call_summariser(self, older: List[_Row]) -> str:
        older = self._truncate_tool_results(older, self.threshold * 2)
        messages = build_messages(older, self.system_prompt)

        if self.context_summary:
            messages.insert(1, {
                "role": "system",
                "content": (
                    "Previous conversation summary (incorporate this into your"
                    f" new summary):\n{self.context_summary}"
                ),
            })

        for msg in messages:
            msg.pop("reasoning_content", None)

        if messages and messages[-1].get("role") == "assistant":
            messages[-1].pop("tool_calls", None)
            if not messages[-1].get("content"):
                messages.pop()

        messages.append({
            "role": "user",
            "content": (
                "The conversation above needs to be summarised because we are "
                "running out of context window. Please write a concise summary "
                "covering:\n"
                "1. Key decisions and conclusions reached\n"
                "2. Important file paths, code changes, and edits made\n"
                "3. Tool calls and their outcomes (condense large outputs to "
                "key findings)\n"
                "4. Current task status and next steps\n\n"
                "Write only the summary, no preamble."
            ),
        })

        _log.debug(f"sending {len(messages)} messages to summariser")

        try:
            response = get_client().chat.completions.create(
                model=self.summary_model,
                messages=messages,
                max_tokens=4096,
            )
        except Exception as exc:
            raise RuntimeError(f"Summarisation failed: {exc}") from exc

        summary = response.choices[0].message.content
        _log.debug(
            f"summary produced ({len(summary)} chars): {summary[:120]}..."
        )
        return summary


__all__ = ["CompactionEngine"]