# Testing Guide

**Purpose**: Testing strategy and test coverage documentation  
**Status**: Active Development

---

## Test Files

### Context Manager Tests
**File**: `nbchat/ui/test_context_manager.py`  
**Status**: 8 tests passing  
**Coverage**: Importance scoring, hard trim scenarios

**Test Scenarios**:
1. Hard Trim Scenarios
   - Test importance-scored eviction (highest score items should survive)
   - Test error_flag protection (if implemented)
   - Test context overflow scenarios
   - Test KEEP_RECENT_EXCHANGES preservation

2. Episodic Store Retrieval
   - Test retrieval by entity reference
   - Test retrieval by importance score
   - Test limit enforcement (L2_RETRIEVAL_LIMIT)
   - Test session isolation

3. Core Memory
   - Test goal persistence
   - Test constraints persistence
   - Test active_entities updates
   - Test error_history updates
   - Test last_correction updates

4. Integration Tests
   - Test full conversation loop with context management
   - Test long-running sessions (>100 turns)
   - Test session restart with task log recovery
   - Test model context overflow prevention

### Database Operations Tests
**File**: `nbchat/core/test_db.py`  
**Status**: 21 tests passing  
**Coverage**: SQLite operations, session management, task log

### Browser Tool Tests
**File**: `nbchat/ui/test_browser.py` (to be created)  
**Status**: 19/19 input validation tests passing  
**Coverage**: Input validation, URL parsing, actions validation

---

## Testing Plan

### Phase 1: Unit Tests (Completed)
- [x] Context manager importance scoring tests
- [x] Database operations tests
- [x] Browser tool input validation tests

### Phase 2: Integration Tests (Pending)
- [ ] Full conversation loop with context management
- [ ] Long-running sessions (>100 turns)
- [ ] Session restart with task log recovery
- [ ] Model context overflow prevention

### Phase 3: End-to-End Tests (Pending)
- [ ] Browser tool reliability tests
- [ ] Tool call streaming tests
- [ ] Error recovery tests
- [ ] Performance tests

---

## Test Scenarios

### Hard Trim Scenarios
**Goal**: Verify importance-scored eviction works correctly

**Test Cases**:
1. Test that highest score items survive hard trim
2. Test that error_flag protected exchanges are not trimmed
3. Test that KEEP_RECENT_EXCHANGES is preserved
4. Test context overflow scenarios

**Expected Behavior**:
```python
# Test 1: Importance-scored eviction
exchanges = [
    {"score": 1.0, "content": "low importance"},
    {"score": 7.0, "content": "error exchange"},
    {"score": 2.5, "content": "success exchange"},
]
trimmed = context_manager.hard_trim(exchanges, max_tokens=100)
assert trimmed[0]["score"] == 7.0  # Error exchange should survive
```

### Episodic Store Retrieval
**Goal**: Verify episodic store retrieval works correctly

**Test Cases**:
1. Test retrieval by entity reference
2. Test retrieval by importance score
3. Test limit enforcement (L2_RETRIEVAL_LIMIT)
4. Test session isolation

**Expected Behavior**:
```python
# Test 1: Retrieval by entity reference
entity = "user_preferences"
results = db.get_episodic_store(entity=entity)
assert len(results) > 0
assert all(r["entity"] == entity for r in results)
```

### Core Memory
**Goal**: Verify core memory persistence works correctly

**Test Cases**:
1. Test goal persistence
2. Test constraints persistence
3. Test active_entities updates
4. Test error_history updates
5. Test last_correction updates

**Expected Behavior**:
```python
# Test 1: Goal persistence
core_memory = db.get_core_memory()
assert core_memory["goal"] == "expected_goal"
```

### Integration Tests
**Goal**: Verify full conversation loop works correctly

**Test Cases**:
1. Test full conversation with context management
2. Test long-running sessions (>100 turns)
3. Test session restart with task log recovery
4. Test model context overflow prevention

**Expected Behavior**:
```python
# Test 1: Full conversation loop
conversation = Conversation()
for i in range(100):
    response = conversation.send(f"Message {i}")
    assert response is not None
```

---

## Test Execution

### Running All Tests
```bash
pytest nbchat/
```

### Running Specific Test File
```bash
pytest nbchat/ui/test_context_manager.py
```

### Running Specific Test
```bash
pytest nbchat/ui/test_context_manager.py::test_importance_scoring
```

### Running Tests with Coverage
```bash
pytest --cov=nbchat nbchat/
```

---

## Test Coverage Goals

| Component | Target Coverage | Current Coverage |
|-----------|----------------|------------------|
| Context Manager | 90% | 75% |
| Database Operations | 90% | 85% |
| Browser Tool | 90% | 50% |
| Compressor | 80% | 60% |
| Conversation | 80% | 40% |

---

## Known Test Issues

### Issue 1: Streaming Tool Call Index Mismatch
**Symptom**: Tests fail when model changes tool call predictions mid-stream

**Root Cause**: OpenAI streaming API limitation when models change tool call predictions

**Current Mitigation**: Added tracking of tool call indices and automatic reset when mismatch is detected

**Long-term Fix Needed**:
1. Implement model-level retry with adjusted prompts
2. Add tool call validation before streaming
3. Consider using non-streaming mode for tool calls
4. Implement graceful degradation when tool call prediction fails

---

## Test Best Practices

1. **Write tests before implementation** - Define expected behavior first
2. **Test edge cases** - Include boundary conditions and error scenarios
3. **Use fixtures** - Set up test data efficiently
4. **Mock external dependencies** - Isolate unit tests from external services
5. **Run tests frequently** - Catch issues early
6. **Document test scenarios** - Explain what each test verifies
7. **Keep tests independent** - Each test should be runnable in isolation
8. **Use descriptive test names** - Make test failures self-explanatory

---

## Test Maintenance

### Before Each Session
1. Run existing test suite to verify no regressions
2. Review test coverage for components being modified
3. Add new tests for new functionality

### After Each Session
1. Update test coverage documentation
2. Document any new test scenarios
3. Note any test failures or flaky tests
4. Push test changes to git

### Regular Maintenance
1. Review and update test scenarios monthly
2. Remove obsolete tests
3. Add tests for newly discovered edge cases
4. Update coverage goals based on project needs