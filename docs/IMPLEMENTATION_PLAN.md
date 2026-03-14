# Implementation Plan

**Status**: Active Development  
**Last Updated**: [Current Date]  
**Purpose**: Single source of truth for all implementation priorities and progress

---

## Current Priorities (Phase 1 - Quick Wins)

### High Priority Tasks (1-2 weeks)

#### ✅ Task 1: Error Flag Protection (COMPLETED)
**Status**: DONE  
**Priority**: HIGH  
**Implementation**: 
- Added `error_flag` field to database schema
- Set error_flag when exchange contains error content
- Use error_flag in importance scoring to protect error exchanges during trimming

**Files Modified**:
- `nbchat/core/db.py` - Added error_flag column to exchanges table
- `nbchat/ui/context_manager.py` - Set error_flag during importance scoring

**Reference**: openclaw's protection of critical exchanges

---

#### 🔄 Task 2: Structured Summary Format (IN PROGRESS)
**Status**: TODO  
**Priority**: HIGH  
**Goal**: Decompose flat summary into structured format (Goal, Entity Delta, Rationale)

**Implementation Plan**:
1. Review current summary generation in context_manager.py
2. Update LLM prompt to output structured JSON format
3. Parse and store as typed blocks: goal, entity_delta, rationale
4. Inject structured summary as dedicated system block

**Current State**:
- Existing prompt in context_manager.py already uses GOAL/, ENTITIES/, RATIONALE: format
- Need to ensure consistent parsing and storage

**Reference**: openclaw's structured memory injection  
**Link**: https://docs.openclaw.ai/concepts/memory

---

#### 🔄 Task 3: Action Verification Mechanism (TODO)
**Status**: TODO  
**Priority**: HIGH  
**Goal**: Implement action verification before execution

**Implementation Plan**:
1. Add verification prompt for high-impact actions
2. Implement state tracking after action execution
3. Add rollback capability for failed actions

**Reference**: openclaw's plugin verification and state tracking

---

## Completed Work (Checklist)

- [x] Review nbchat/ folder code
- [x] Review SOTA_Autonomous_Agent_Review.md documentation
- [x] Review openclaw project repository
- [x] Review browser tool implementation
- [x] Review context management implementation
- [x] Fixed browser tool - Playwright installation completed
- [x] Implemented retry policy for tool calls (openclaw-inspired)
- [x] Added error_flag field for protected exchanges
- [x] Updated context_manager.py to protect error exchanges during trimming
- [x] Implemented importance scoring for tool exchanges
- [x] Implemented hard-trim with importance-scored eviction

---

## Context Management Testing

### Completed Tests
- [x] Unit tests for context manager importance scoring (nbchat/ui/test_context_manager.py) - 8 tests passing
- [x] Unit tests for database operations (nbchat/core/test_db.py) - 21 tests passing

### Pending Tests
- [ ] Test hard trim scenarios (importance-scored eviction)
- [ ] Test error_flag protection
- [ ] Test context overflow scenarios
- [ ] Test KEEP_RECENT_EXCHANGES preservation
- [ ] Test episodic store retrieval by entity reference
- [ ] Test episodic store retrieval by importance score
- [ ] Test limit enforcement (L2_RETRIEVAL_LIMIT)
- [ ] Test session isolation
- [ ] Test core memory goal persistence
- [ ] Test core memory constraints persistence
- [ ] Test full conversation loop integration
- [ ] Test long-running sessions (>100 turns)
- [ ] Test session restart with task log recovery

---

## Browser Tool Status

### Phase 1: Input Validation (COMPLETED)
- [x] Add input validation for `url` parameter
- [x] Add input validation for `actions` parameter
- [x] Add input validation for `kwargs` handling
- [x] Add structured error handling with detailed error messages
- [x] Write tests to verify all input validation works correctly
- [x] Verify all validation edge cases

**Status**: 19/19 input validation tests passing

### Phase 2: Core Feature Stability (TODO)
- [ ] Ensure `click` action works reliably
- [ ] Ensure `type` action works reliably
- [ ] Ensure `select` action works reliably
- [ ] Ensure `wait` action works reliably
- [ ] Ensure `scroll` action works reliably
- [ ] Ensure `navigate` action works reliably
- [ ] Ensure `screenshot` action works reliably
- [ ] Write comprehensive tests for all action types

### Phase 3: Content Extraction (TODO)
- [ ] Ensure selector-based extraction works
- [ ] Ensure full page extraction with `extract_elements` works
- [ ] Ensure response JSON structure is consistent and valid
- [ ] Write tests for content extraction scenarios

### Phase 4: Reliability & Error Handling (TODO)
- [ ] Implement retry logic with exponential backoff
- [ ] Add timeout configuration validation
- [ ] Improve error messages with actionable hints
- [ ] Write tests for error scenarios and retry logic

### Phase 5: Advanced Features (TODO)
- [ ] Add JavaScript evaluation support
- [ ] Add session/persistent browser support
- [ ] Add comprehensive logging and debugging tools
- [ ] Performance optimization and resource management

---

## Known Issues & Failure Modes

### Issue: Streaming Tool Call Index Mismatch
**Symptom**: `APIError: Invalid diff: now finding less tool calls!`

**Root Cause**: Model predicts multiple tool calls in initial streaming tokens, then changes mind and reduces the number of tool calls.

**Current Mitigation**: Added tracking of tool call indices and automatic reset when mismatch is detected.

**Long-term Fix Needed**:
1. Implement model-level retry with adjusted prompts
2. Add tool call validation before streaming
3. Consider using non-streaming mode for tool calls
4. Implement graceful degradation when tool call prediction fails

**Reference**: Known limitation in OpenAI's streaming API when models change tool call predictions mid-stream.

---

## Session Handoff Checklist

Before ending a session:
1. ✅ Update progress in this document
2. ✅ Update specific component documentation if changes made
3. ✅ Push changes to git
4. ✅ Document any blockers or unresolved issues
5. ✅ Note next steps for next session

---

## References

### OpenClaw Project
- Repository: https://github.com/openclaw/openclaw
- Vision: https://github.com/openclaw/openclaw/blob/main/VISION.md
- Docs: https://docs.openclaw.ai
- Security: https://github.com/openclaw/openclaw/blob/main/SECURITY.md
- Retry: https://docs.openclaw.ai/concepts/retry
- Model Failover: https://docs.openclaw.ai/concepts/model-failover
- Session Pruning: https://docs.openclaw.ai/concepts/session-pruning
- Presence: https://docs.openclaw.ai/concepts/presence
- Plugins: https://docs.openclaw.ai/tools/plugin.md
- MCP Support: https://github.com/steipete/mcporter
- Browser Tool: https://docs.openclaw.ai/tools/browser

### Academic References
- MemGPT: Towards LLMs as Operating Systems (Packer et al., 2023)
- Letta Memory Blocks (2024-2025)
- A-MEM: Agentic Memory for LLM Agents (Xu et al., NeurIPS 2025)
- AgeMem: Agentic Memory - Unified Long-Term and Short-Term Memory Management
- TRIM-KV: Cache What Lasts (NeurIPS 2025)
- HippoRAG: Neurobiologically Inspired Long-Term Memory (Gutierrez et al., NeurIPS 2024)

---

## Working Principles

All concepts and ideas MUST include:
1. **Source references** (GitHub links, papers, documentation URLs)
2. **Sample code snippets** or implementation patterns
3. **Clear attribution** of inspiration
4. **No lazy statements** - every plan must be backed by research

**Why this matters**: Setting the right goals requires deep understanding of what SOTA implementations actually exist in the commercial and open source communities.