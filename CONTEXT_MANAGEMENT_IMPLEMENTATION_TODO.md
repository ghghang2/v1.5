# Context Management Implementation TODO

## Overview

This document details all upgrades, enhancements, and improvements that nbchat's context management system can benefit from. Each item includes specific references to relevant code files and background information for the engineering team.

**Last Updated:** 2026-03-16
**Status:** Planning Phase

---

## Executive Summary

nbchat currently implements a **5-layer context management system** (L0-L2 + Prior Context + Hard Trim) that maintains context across ultra-long agentic loops. The system uses SQLite-based persistence with importance scoring for intelligent eviction.

While the current implementation is functional, several opportunities exist for:
1. **Enhanced retrieval effectiveness** (better semantic search, vector indexing)
2. **Improved summarization quality** (chain-of-thought, structured outputs)
3. **Better entity tracking** (more sophisticated NER, type hierarchy)
4. **Adaptive behavior** (learn from usage patterns)
5. **Debuggability and observability** (better logging, metrics)
6. **Resilience and robustness** (failure recovery, data integrity)

---

## Priority 1: High-Impact Quick Wins

### 1.1 Entity Extraction Enhancement

**Current State:**
- `_extract_entities()` in `nbchat/ui/context_manager.py` (lines 87-114) uses regex patterns to extract file paths, API paths, and URLs
- Limited to 10 entities per extraction
- No type hierarchy or semantic understanding

**Problem:**
- Regex-based extraction misses semantic entity relationships
- No distinction between file types (read vs write vs execute)
- No handling of entity aliases or variations
- No entity deduplication beyond simple set membership

**Recommended Improvements:**

1. **Add entity type tagging**
   ```python
   # Proposed new return format
   class Entity:
       name: str              # e.g., "file:nbchat/ui/context_manager.py"
       type: str              # "file", "api", "url", "task", "error"
       subtype: str           # "python_file", "rest_api", "file_path"
       access: str            # "read", "write", "create", "execute"
       confidence: float      # 0.0-1.0 confidence score
   ```

   **Reference:** `nbchat/ui/context_manager.py:87-114`

2. **Implement entity alias tracking**
   - Maintain mapping of common aliases to canonical forms
   - Example: "utils" → "nbchat/core/utils.py"
   - Store in `session_meta` table

3. **Add file operation context**
   - Track operations: read, write, create, delete, modify
   - Store in `episodic_store.action_type` with more granularity

**Implementation Location:**
- `nbchat/ui/context_manager.py:87-114` - `_extract_entities()` function
- `nbchat/core/db.py` - Consider adding `entity_aliases` column to `core_memory` table

**Background Reading:**
- Current extraction logic: `nbchat/ui/context_manager.py:87-114`
- Entity storage: `nbchat/core/db.py:67-82` (episodic_store schema)

**Reference:**
- See Beads repository for entity tracking patterns: `beads.go` context handling

**Effort:** 2-3 days
**Impact:** HIGH - Improves retrieval accuracy and context relevance

---

### 1.2 Importance Scoring Refinement

**Current State:**
- `_importance_score()` in `nbchat/ui/context_manager.py` (lines 144-192)
- Score range: 0.0-10.0
- Key factors: errors (+3.0), tool results (+1.0-3.0), corrections (+2.5)
- `L2_WRITE_THRESHOLD = 2.0` (lowered from 3.5)

**Problem:**
- Binary error detection (any error keyword = high score)
- No consideration of error severity or type
- Success indicators are simple keyword matching
- No temporal decay for old successful exchanges
- No distinction between informational vs actionable content

**Recommended Improvements:**

1. **Add error severity classification**
   ```python
   def _classify_error_severity(error_msg: str) -> float:
       """Return 1.0-5.0 based on error severity"""
       critical_patterns = ["fatal", "out of memory", "segfault"]
       warning_patterns = ["warning", "deprecated", "slow"]
       error_patterns = ["error", "exception", "failed"]
       info_patterns = ["info", "notice", "debug"]
       
       for pattern in critical_patterns:
           if pattern in error_msg.lower():
               return 5.0
       for pattern in warning_patterns:
           if pattern in error_msg.lower():
               return 3.0
       for pattern in error_patterns:
           if pattern in error_msg.lower():
               return 2.0
       return 1.0
   ```

2. **Add temporal decay**
   - Older successful exchanges decay in importance
   - Implement exponential decay: `score *= 0.999` per day
   - Prevents old successful exchanges from dominating retrieval

3. **Add content quality scoring**
   - Information density (tokens vs meaningful content)
   - Code quality indicators (for code tools)
   - Novelty factor (new patterns vs common operations)

4. **Add multi-factor weighting**
   ```python
   # Proposed scoring formula
   final_score = (
       base_score * 0.3 +
       error_severity * 0.25 +
       temporal_factor * 0.15 +
       quality_score * 0.15 +
       novelty_score * 0.15
   )
   ```

**Implementation Location:**
- `nbchat/ui/context_manager.py:144-192` - `_importance_score()` static method
- `nbchat/core/db.py:75` - Consider adding `score_timestamp` to `episodic_store`

**Background Reading:**
- Current scoring: `nbchat/ui/context_manager.py:144-192`
- Scoring constants: `nbchat/ui/context_manager.py:45-53`

**Reference:**
- Compresr importance scoring patterns from `docs/context-gateway-architecture-summary.md`

**Effort:** 3-4 days
**Impact:** HIGH - More intelligent eviction and retention

---

### 1.3 Episodic Store Query Optimization

**Current State:**
- `query_episodic_by_entities()` in `nbchat/core/db.py` (lines 267-293)
- Uses LIKE pattern matching on JSON-encoded entity_refs
- Limited to 5 results by default
- No semantic understanding of entity relationships

**Problem:**
- LIKE matching is substring-based, not semantic
- No support for fuzzy matching
- No support for multi-entity queries
- No support for temporal queries (recent vs historical)

**Recommended Improvements:**

1. **Add vector-based similarity search**
   - Encode entity references as embeddings (use existing model or lightweight embedding)
   - Store embeddings in new `episodic_embeddings` table
   - Use cosine similarity for semantic search

2. **Add query types**
   ```python
   class EpisodicQuery:
       type: str           # "by_entities", "by_importance", "by_temporal", "hybrid"
       entities: List[str] # Entity references
       min_score: float    # Minimum importance threshold
       time_range: str     # "last_1h", "last_24h", "last_week"
       include_semantic: bool  # Use semantic search
   ```

3. **Add fuzzy matching**
   - Implement Levenshtein distance or Jaro-Winkler for entity matching
   - Configurable threshold (e.g., match entities that are 80% similar)

4. **Add full-text search index**
   - Create FTS5 index on `outcome_summary` field
   - Enable keyword-based retrieval without entity matching

**Implementation Location:**
- `nbchat/core/db.py:67-82` - Episodic store schema
- `nbchat/core/db.py:267-293` - `query_episodic_by_entities()` function
- New: `nbchat/core/db.py` - `query_episodic_hybrid()` function

**Schema Changes Required:**
```sql
-- Add to episodic_store
ALTER TABLE episodic_store ADD COLUMN embedding BLOB;

-- New table for embeddings
CREATE TABLE IF NOT EXISTS episodic_embeddings (
    id              INTEGER PRIMARY KEY,
    session_id      TEXT NOT NULL,
    embedding_dims  INTEGER NOT NULL,  -- e.g., 768 for most models
    embedding_model TEXT NOT NULL,      -- Track model version
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast filtering
CREATE INDEX IF NOT EXISTS idx_episodic_session_score 
ON episodic_store(session_id, importance_score DESC);
```

**Background Reading:**
- Current query: `nbchat/core/db.py:267-293`
- Query limits: `nbchat/ui/context_manager.py:50` (`L2_RETRIEVAL_LIMIT = 5`)

**Reference:**
- Vector search patterns from openclaw repository (see `SOTA_Agent_Review_Progress.md`)

**Effort:** 5-7 days
**Impact:** HIGH - Dramatically improves retrieval quality

---

## Priority 2: Medium-Impact Enhancements

### 2.1 Summarization Quality Improvement

**Current State:**
- `_call_summarizer()` in `nbchat/ui/context_manager.py` (lines 533-556)
- Uses `_STRUCTURED_SUMMARY_PROMPT` (lines 59-74)
- Output format: GOAL/ENTITIES/RATIONALE three-line structure
- LLM called per turn for prior context

**Problem:**
- Simple three-line format may lose important details
- No chain-of-thought prompting for better reasoning
- No validation of output format
- No caching of similar turn summaries
- No handling of ambiguous or unclear turns

**Recommended Improvements:**

1. **Add chain-of-thought prompting**
   ```python
   CHAIN_OF_THOUGHT_PROMPT = """
   Analyze this conversation segment step by step before providing the final summary.
   
   For each step:
   1. Identify the user's apparent goal
   2. Identify what tools/actions were taken
   3. Identify any errors or unexpected outcomes
   4. Synthesize the actual outcome vs expected outcome
   
   After your step-by-step analysis, provide EXACTLY three lines:
   GOAL: <one sentence>
   ENTITIES: <pipe-separated entity changes, or 'none'>
   RATIONALE: <one sentence about key action and outcome>
   
   Output exactly these three lines, no preamble or extra text.
   """
   ```

2. **Add output validation**
   - Parse output with retry logic
   - Fallback to simpler prompt if structured output fails
   - Log parsing failures for debugging

3. **Implement similarity-based summarization caching**
   ```python
   def _get_turn_summary(self, unit: List[_Row]) -> str:
       # Hash content
       content_hash = hashlib.sha1("".join(r[1] + r[4] for r in unit).encode()).hexdigest()
       
       # Check cache
       cached = self._turn_summary_cache.get(content_hash)
       if cached:
           return cached
       
       # Check for similar units (semantic similarity)
       similar = self._find_similar_units(unit, threshold=0.85)
       if similar:
           return similar[0]["summary"]  # Return cached similar summary
       
       # Call LLM
       summary = self._call_summarizer(unit)
       
       # Cache
       self._turn_summary_cache[content_hash] = summary
       return summary
   ```

4. **Add multi-turn context awareness**
   - When summarizing a turn, also consider adjacent turns
   - Group related turns into single summary units
   - Detect multi-turn operations (e.g., search → analyze → fix)

**Implementation Location:**
- `nbchat/ui/context_manager.py:533-556` - `_call_summarizer()` method
- `nbchat/ui/context_manager.py:533` - `_get_turn_summary()` method
- `nbchat/ui/context_manager.py:461-490` - `_build_prior_context()` method

**Prompt Updates:**
- `nbchat/ui/context_manager.py:59-74` - `_STRUCTURED_SUMMARY_PROMPT` constant

**Effort:** 3-4 days
**Impact:** MEDIUM-HIGH - Better context preservation

---

### 2.2 L1 Core Memory Enhancement

**Current State:**
- `_get_l1_block()` in `nbchat/ui/context_manager.py` (lines 196-225)
- Slots: goal, constraints, active_entities, error_history, last_correction
- Stored in `core_memory` table (lines 84-92 of db.py)

**Problem:**
- No structured representation of constraints (currently JSON dump)
- Error history is flat text list, no classification
- Active entities is simple list, no relationships
- No proactive goal refinement (goal is static until user correction)

**Recommended Improvements:**

1. **Structured constraint representation**
   ```python
   class Constraints:
       type: str              # "must", "must_not", "preference", "suggestion"
       description: str
       priority: int          # 1-5, 1=highest
       source: str            # "user", "system", "auto-detected"
   ```

2. **Error classification and grouping**
   ```python
   class ErrorGroup:
       category: str          # "network", "parsing", "authentication", "system"
       frequency: int         # How many times occurred
       severity: str          # "critical", "high", "medium", "low"
       resolved: bool         # Has it been resolved
       last_occurrence: datetime
   ```

3. **Entity relationship tracking**
   ```python
   class Entity:
       identifier: str        # e.g., "file:utils.py"
       type: str              # "file", "api", "url", "task"
       relationships: List[str]  # Related entities
       state: str             # "created", "modified", "deleted", "viewed"
   ```

4. **Auto-goal refinement**
   - Monitor session progress toward goal
   - Suggest goal adjustments based on progress
   - Track goal achievement indicators

**Implementation Location:**
- `nbchat/ui/context_manager.py:196-225` - `_get_l1_block()` method
- `nbchat/ui/context_manager.py:226-254` - `_update_l1_goal_from_user()` method
- `nbchat/ui/context_manager.py:255-278` - `_update_l1_from_exchange()` method
- `nbchat/core/db.py:84-92` - `core_memory` table schema

**Schema Updates Required:**
```sql
-- Alter core_memory table for structured data
-- Store JSON with defined schema, document schema in schema migrations

-- New table for error groups
CREATE TABLE IF NOT EXISTS error_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    frequency INTEGER DEFAULT 1,
    severity TEXT DEFAULT 'medium',
    resolved INTEGER DEFAULT 0,
    last_occurrence TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES core_memory(session_id)
);
```

**Effort:** 4-5 days
**Impact:** MEDIUM - Better structured memory

---

### 2.3 Context Window Management Optimization

**Current State:**
- `_window()` method in `nbchat/ui/context_manager.py` (lines 391-457)
- L0: Last WINDOW_TURNS user turns
- Secondary trim: Count only non-analysis rows against MAX_WINDOW_ROWS
- Prefix: L1 block, L2 block, prior context (system rows)

**Problem:**
- No consideration of content importance during window selection
- Analysis rows (reasoning traces) excluded but could be useful
- No adaptive window sizing based on task complexity
- No pre-fetching strategy for anticipated context

**Recommended Improvements:**

1. **Importance-aware window selection**
   ```python
   def _select_window_rows(self, candidate_rows: List[_Row], budget: int) -> List[_Row]:
       # Score each row
       scored_rows = []
       for row in candidate_rows:
           score = self._score_window_row(row)
           scored_rows.append((score, row))
       
       # Sort by importance
       scored_rows.sort(key=lambda x: x[0], reverse=True)
       
       # Select top rows until budget exhausted
       result = []
       for score, row in scored_rows:
           if self._row_estimates_tokens(row) <= budget:
               result.append(row)
               budget -= self._row_estimates_tokens(row)
           else:
               break
       
       return result
   ```

2. **Analysis row value retention**
   - Don't exclude analysis rows; score them too
   - Reasoning traces may contain important insights
   - Apply lighter compression to analysis rows

3. **Adaptive window sizing**
   ```python
   def _get_adaptive_window_size(self, current_task: dict) -> int:
       # Base size
       window
   ```

4. **Pre-fetching strategy**
   - Identify context needed for anticipated next actions
   - Proactively retrieve relevant prior context

**Implementation Location:**
- `nbchat/ui/context_manager.py:391-457` - `_window()` method
- `nbchat/ui/context_manager.py:461-490` - `_build_prior_context()` method

**Background Reading:**
- Window constants: `nbchat/ui/context_manager.py:39-44`
- Current window implementation: `nbchat/ui/context_manager.py:391-457`

**Effort:** 3-4 days
**Impact:** MEDIUM - Better context utilization

---

### 2.4 Tool Call Validation and Consistency

**Current State:**
- Tool calls are accumulated in `tool_buffer` dict keyed by `tc.index`
- SDK diff error: "Invalid diff: now finding less tool calls!"
- Error handling in `_stream_response()` catches and re-raises SDK errors

**Problem:**
- Tool call index management may be inconsistent
- SDK validates tool call structure across chunks
- Partial/late-arriving tool calls may cause validation failures
- No validation of tool call index consistency before sending to SDK

**Recommended Improvements:**

1. **Add tool call index validation**
   ```python
   def _validate_tool_buffer(self, tool_buffer: dict) -> None:
       """Validate tool buffer for SDK compatibility"""
       indices = sorted(tool_buffer.keys())
       expected = list(range(1, len(indices) + 1))
       
       if indices != expected:
           _log.error(
               f"Tool buffer indices inconsistent: {indices}. "
               f"Expected: {expected}"
           )
       
       # Verify no duplicate indices
       if len(indices) != len(set(indices)):
           _log.error("Duplicate tool call indices detected")
       
       # Verify ascending order
       for i in range(1, len(indices)):
           if indices[i] <= indices[i-1]:
               _log.error(f"Non-ascending tool call indices: {indices[i-1]} >= {indices[i]}")
   ```

2. **Add tool call deduplication**
   - Check for duplicate tool call content before sending
   - Use content hash for deduplication

3. **Add tool call ordering validation**
   - Ensure tool calls are ordered by index before accumulation
   - Validate after each chunk processing

4. **Buffer synchronization**
   - Ensure tool buffer is synchronized with actual tool call state
   - Add timeout/heartbeat checks for stragglers

**Implementation Location:**
- `nbchat/ui/conversation.py:260-320` - `_stream_response()` method
- `nbchat/ui/conversation.py:193-201` - `tool_buffer` management

**Reference:**
- SDK diff error handling: `nbchat/ui/conversation.py:298-310`
- Tool call accumulation: `nbchat/ui/conversation.py:270-278`

**Effort:** 1-2 days
**Impact:** HIGH - Fixes SDK diff errors

---

### 2.5 Compression Resilience

**Current State:**
- Tool output is compressed before being sent to model
- Error detection happens on `raw_result` before compression
- Some error signals may be lost in compression

**Problem:**
- Compression may strip important error signals
- Model may see "NO_RELEVANT_OUTPUT" for error cases
- No fallback mechanism if compression fails

**Recommended Improvements:**

1. **Add compression error handling**
   ```python
   def _call_compressor(self, tool_name: str, tool_args: str, raw_result: str) -> str:
       try:
           return comp.compress_tool_output(...)
       except Exception as exc:
           _log.error(f"Compression failed for {tool_name}: {exc}")
           # Fallback: return raw result or truncated version
           return raw_result[:1000] + " [truncated due to compression error]"
   ```

2. **Add post-compression error check**
   - Re-check compressed output for error signals
   - Use both raw and compressed for error detection

3. **Add compression quality metrics**
   - Track compression ratio per tool
   - Flag potential information loss

**Implementation Location:**
- `nbchat/ui/context_manager.py:436-457` - compression logic
- `nbchat/core/compressor.py` - compression module

**Background Reading:**
- Current compression: `nbchat/ui/context_manager.py:436-457`
- Error flag logic: `nbchat/ui/context_manager.py:427-430`

**Effort:** 2-3 days
**Impact:** MEDIUM - Better error handling

---

## Priority 3: Long-term Vision

### 3.1 Persistent Context Learning

**Concept:**
- Learn from successful context selections
- Adapt context window based on past performance
- Maintain a model of "good" vs "bad" context

**Implementation Ideas:**
- Record context window composition for each successful turn
- Use this data to inform future window selections
- Implement bandit-style exploration for context selection

**Effort:** 2-3 months
**Impact:** HIGH - Adaptive, self-improving context management

---

### 3.2 Multi-Session Context

**Concept:**
- Connect related sessions through shared context
- Persist important decisions across sessions
- Provide session continuity without full context transfer

**Implementation Ideas:**
- Session linking via entity relationships
- Goal persistence and transfer
- Error history sharing across related sessions

**Effort:** 3-4 months
**Impact:** MEDIUM - Improved long-term task management

---

### 3.3 Dynamic Context Archival

**Concept:**
- Automatically archive less relevant context to long-term storage
- On-demand retrieval of archived content
- Smart retention policies

**Implementation Ideas:**
- Periodic context review and archival
- Trigger-based archival (e.g., after successful completion)
- Archival tiering (hot/warm/cold storage)

**Effort:** 2-3 months
**Impact:** MEDIUM - Better context window management

---

## Implementation Prioritization Matrix

| Item | Effort | Impact | Priority Score |
|------|--------|--------|----------------|
| 1.3 Episodic Query Optimization | 5-7 days | HIGH | 8.0 |
| 2.4 Tool Call Validation | 1-2 days | HIGH | 7.0 |
| 1.1 Entity Extraction | 2-3 days | HIGH | 6.3 |
| 1.2 Importance Scoring | 3-4 days | HIGH | 6.0 |
| 2.3 Context Window Optimization | 3-4 days | MEDIUM | 4.0 |
| 2.1 Summarization Quality | 3-4 days | MEDIUM-HIGH | 4.5 |
| 2.2 L1 Core Memory Enhancement | 4-5 days | MEDIUM | 3.5 |
| 2.5 Compression Resilience | 2-3 days | MEDIUM | 4.0 |
| 3.1 Persistent Context Learning | 2-3 months | HIGH | 6.5 |
| 3.2 Multi-Session Context | 3-4 months | MEDIUM | 4.0 |
| 3.3 Dynamic Context Archival | 2-3 months | MEDIUM | 4.0 |

**Recommended Starting Points:**
1. **2.4 Tool Call Validation** (1-2 days, HIGH impact) - Fixes immediate SDK errors
2. **1.1 Entity Extraction** (2-3 days, HIGH impact) - Quick win for retrieval quality
3. **1.2 Importance Scoring** (3-4 days, HIGH impact) - Better eviction strategy

---

## Technical Debt

- **SDK compatibility**: OpenAI SDK validation requirements for tool calls
- **Memory leak potential**: `tool_buffer` may grow without bounds
- **Error propagation**: Error signals may be lost through multiple layers

---

## References

- Beads repository context handling: `beads.go`
- Compresr architecture: `docs/context-gateway-architecture-summary.md`
- Openclaw vector search patterns: `SOTA_Agent_Review_Progress.md`