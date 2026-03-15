# Expand on Demand and Intent-aware Filtering - Implementation TODO

## Overview

This TODO tracks the implementation of two features from Compresr's Context Gateway:
1. **Expand on Demand** - HIGH PRIORITY
2. **Intent-aware Filtering** - MEDIUM PRIORITY

Both features complement nbchat's existing multi-layer context management (L0-L2).

## Feature Descriptions

### 1. Expand on Demand

**Problem:** Once content is compressed or truncated in nbchat, it cannot be retrieved if the model needs more detail.

**Solution:** Implement a cache of original outputs that can be retrieved via an `expand()` method when the LLM requests more detail.

**Components:**
- OutputCompressor: Track original outputs with metadata
- ExpandCache: In-memory or SQLite-backed cache with TTL
- Integration: Add expand logic to context manager
- Metrics: Track expansion requests and compression ratios

### 2. Intent-aware Filtering

**Problem:** File/command tools always use head+tail truncation, even when output is clearly irrelevant to current task.

**Solution:** Add lightweight intent detection that analyzes tool call arguments and filters output accordingly.

**Components:**
- IntentClassifier: Simple regex/keyword-based intent detection
- FilterCompressor: Apply filtering for specific tools (grep, file reads)
- Fallback: Head+tail truncation when filtering not applicable
- Testing: Ensure no information loss from important content

---

## Implementation Phases

### Phase 1: Expand on Demand (Week 1)

#### Task 1.1: Add Expand Cache to OutputCompressor
- [ ] Modify OutputCompressor class to cache original outputs
- [ ] Store metadata: tool_call_id, original, compressed, tool_name, timestamps
- [ ] Implement expand() method to retrieve original content
- [ ] Add TTL support for cache entries
- [ ] Add compression ratio metrics

**File:** nbchat/core/compressor.py

**Estimated:** 2-3 hours

#### Task 1.2: Add Expand Cache Layer
- [ ] Create ExpandCache class with in-memory + SQLite persistence
- [ ] Implement TTL-based eviction
- [ ] Add thread safety
- [ ] Test cache operations

**File:** nbchat/core/expand_cache.py

**Estimated:** 2-3 hours

#### Task 1.3: Integrate Expand with Context Manager
- [ ] Add expand tracking to message context
- [ ] Add expand requests to context manager
- [ ] Update compression logging
- [ ] Add expand metrics to inference_metrics.log

**File:** nbchat/ui/context_manager.py

**Estimated:** 2-3 hours

#### Task 1.4: Add Unit Tests
- [ ] Test expand cache CRUD operations
- [ ] Test expand integration with compressor
- [ ] Test TTL and eviction
- [ ] Test thread safety

**File:** nbchat/core/test_expand_cache.py

**Estimated:** 2-3 hours

**Phase 1 Total:** 8-12 hours

---

### Phase 2: Intent-aware Filtering (Week 1-2)

#### Task 2.1: Implement Intent Classifier
- [ ] Create IntentClassifier class with simple regex/keyword detection
- [ ] Support grep pattern analysis
- [ ] Support file path relevance checking
- [ ] Add configuration for custom patterns
- [ ] Add logging for intent detection decisions

**File:** nbchat/core/intent_classifier.py

**Estimated:** 3-4 hours

#### Task 2.2: Implement Filter Compressor
- [ ] Modify compress_tool_output to check for intent filtering
- [ ] Add filter_compressed() method for grep results
- [ ] Add filter_file_content() for file reads
- [ ] Maintain fallback to head+tail when filtering not applicable
- [ ] Update ALWAYS_KEEP_TOOLS list if needed

**File:** nbchat/core/compressor.py

**Estimated:** 3-4 hours

#### Task 2.3: Integrate with Context Management
- [ ] Update compressor logging to show intent decisions
- [ ] Add filtering metrics to inference_metrics.log
- [ ] Add configuration for filtering behavior
- [ ] Test with various tool types

**File:** nbchat/ui/context_manager.py (optional)

**Estimated:** 2-3 hours

#### Task 2.4: Add Unit Tests
- [ ] Test intent classifier with various patterns
- [ ] Test filter compressor with sample outputs
- [ ] Test edge cases (empty output, special characters)
- [ ] Test fallback behavior

**File:** nbchat/core/test_intent_classifier.py

**Estimated:** 2-3 hours

**Phase 2 Total:** 10-14 hours

---

## Testing Plan

### Unit Tests
- [ ] Expand cache operations
- [ ] Intent classification accuracy
- [ ] Filter compressor effectiveness
- [ ] Fallback behavior for all edge cases

### Integration Tests
- [ ] End-to-end compression with expand
- [ ] End-to-end filtering with various tool types
- [ ] Context manager integration

### Performance Tests
- [ ] Cache memory usage
- [ ] Intent classifier latency
- [ ] Compression time with/without filtering

---

## Configuration

### repo_config.yaml additions

```yaml
# Expand on Demand settings
expand_on_demand:
  enabled: true
  cache_ttl_minutes: 60  # Default: 60 minutes
  max_cache_size_mb: 100  # Memory limit for cache

# Intent-aware filtering settings
intent_filtering:
  enabled: true
  tools:
    grep:
      enabled: true
      sensitivity: medium  # low, medium, high
    file_read:
      enabled: true
      context_window: 500  # Characters of context to consider
  fallback_to_truncation: true  # Always fall back if filtering fails
```

---

## Metrics to Track

### Expand on Demand Metrics
- Total compression ratio (original/compressed)
- Total expansion requests
- Average time between compression and expansion
- Cache hit rate
- Memory usage of expand cache

### Intent-aware Filtering Metrics
- Number of tools filtered vs truncated
- False positive rate (important content filtered out)
- False negative rate (irrelevant content kept)
- Intent classification accuracy
- Compression ratio improvement

---

## Rollback Plan

If issues arise:
1. Feature flags can disable intent filtering
2. Expand cache can be disabled if memory issues occur
3. Fallback to existing head+tail truncation for all tools

---

## Dependencies

- nbchat/core/config.py - For configuration handling
- nbchat/core/db.py - For SQLite storage
- nbchat/ui/context_manager.py - For context management integration
- nbchat/core/compressor.py - Current compression logic

---

## Success Criteria

1. Expand on Demand:
   - [ ] Original content can be retrieved after compression
   - [ ] Cache doesn't grow unbounded
   - [ ] Metrics show compression ratios
   - [ ] Tests pass

2. Intent-aware Filtering:
   - [ ] Irrelevant content is filtered out for grep
   - [ ] Relevant content is preserved
   - [ ] No false positives for important information
   - [ ] Fallback works when filtering fails
   - [ ] Tests pass

---

*Last Updated: 2026-03-15*
