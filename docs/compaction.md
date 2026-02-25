# Automatic Context Compaction

## Purpose

Large language models have a finite token limit. When a conversation grows long, older messages must be summarized so that the most recent context can fit within the model’s context window.

---

## Core Components

| File | Responsibility |
|------|----------------|
| `nbchat/compaction.py` | Implements `CompactionEngine`, the heart of the compaction logic. |
| `nbchat/ui/chatui.py` | Instantiates `CompactionEngine` and triggers it during conversation flow. |
| `nbchat/core/config.py` | Holds compaction‑related constants (`CONTEXT_TOKEN_THRESHOLD`, `TAIL_MESSAGES`, `SUMMARY_PROMPT`). |
