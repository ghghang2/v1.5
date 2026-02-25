# Automatic Context Compaction

## Purpose

Large language models have a finite token limit. When a conversation grows long, older messages must be summarized so that the most recent context can fit within the model's context window.  This repository implements a lightweight compaction strategy that:

1. **Detects** when the token estimate of the conversation history is approaching the model's limit.
2. **Summarizes** the oldest portion of the history using a secondary summarization model.
3. **Reinjects** the summary as a single system‑like message called `compacted` and keeps the most recent *N* messages verbatim.

The goal is to preserve the essential information while keeping the token count within a safe margin.

---

## Core Components

| File | Responsibility |
|------|----------------|
| `nbchat/compaction.py` | Implements `CompactionEngine`, the heart of the compaction logic.
| `nbchat/ui/chatui.py` | Instantiates `CompactionEngine` and triggers it during conversation flow.
| `nbchat/core/config.py` | Holds compaction‑related constants (`CONTEXT_TOKEN_THRESHOLD`, `TAIL_MESSAGES`, `SUMMARY_PROMPT`).
