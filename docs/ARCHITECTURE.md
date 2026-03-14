# System Architecture

**Purpose**: Comprehensive analysis of current architecture vs SOTA patterns  
**Status**: Reference Document

---

## Executive Summary

This document provides a comprehensive review of the nbchat autonomous agent project, analyzing current capabilities against state-of-the-art (SOTA) patterns from openclaw and related projects.

---

## Current Architecture Analysis

### Strengths

1. **Robust Context Management**
   - Three-layer approach (tool compression, task log, hard trim) is well-designed
   - Deterministic task log prevents catastrophic forgetting
   - Token budget management is sophisticated and reliable

2. **Tool Execution Framework**
   - ThreadPoolExecutor for parallel tool execution
   - Automatic tool discovery via module scanning
   - Schema generation from function signatures

3. **Persistence Layer**
   - SQLite-based chat history with session management
   - Session metadata storage for context summaries and caches
   - Task log survives kernel restarts

4. **Streaming Response Handling**
   - Real-time streaming with reasoning_content support
   - Proper tool call handling in streaming chunks
   - UI rendering of intermediate states

### Weaknesses & Opportunities

1. **Limited Self-Reflection**
   - No mechanism for the agent to review its own actions
   - No error recovery or retry strategies
   - No learning from past failures

2. **Single-Model Dependency**
   - All operations use the same model
   - No model selection based on task complexity
   - No ensemble or verification mechanisms

3. **Limited Planning Capabilities**
   - No explicit planning phase before execution
   - No task decomposition or subgoal generation
   - Reactive rather than proactive behavior

4. **Missing Memory Systems**
   - No long-term memory across sessions
   - No knowledge base or fact storage
   - No preference learning

5. **Limited Multi-Agent Patterns**
   - No specialized agents for different tasks
   - No agent collaboration or delegation
   - No role-based specialization

---

## SOTA Patterns from openclaw & Related Projects

### 1. Recursive Self-Improvement (RSI)

**Concept**: Agents that can modify their own code, prompts, and configurations to improve performance.

**Key Components**:
- Code modification tools with safety checks
- Automated testing before applying changes
- Version control integration for rollback
- Performance tracking to measure improvements

**Refactoring Impact**: HIGH  
**Implementation Effort**: MEDIUM  
**Recommendation**: IMPLEMENT

**Implementation Plan**:
```python
# Add self-improvement capabilities
class SelfImprovementEngine:
    def __init__(self, agent):
        self.agent = agent
        self.version_control = GitIntegration()
        self.test_suite = TestRunner()
        
    def propose_improvement(self, feedback):
        """Generate code changes based on feedback"""
        # Use agent to analyze feedback and propose changes
        pass
    
    def apply_improvement(self, changes):
        """Safely apply improvements with testing"""
        # Run tests before applying
        # Commit to version control
        # Monitor performance impact
        pass
```

### 2. Hierarchical Task Planning

**Concept**: Break complex tasks into subgoals and plan execution order.

**Key Components**:
- Task decomposition before execution
- Dependency graph for tool calls
- Milestone tracking
- Adaptive replanning when obstacles arise

**Refactoring Impact**: HIGH  
**Implementation Effort**: MEDIUM  
**Recommendation**: IMPLEMENT

**Implementation Plan**:
```python
# Add planning layer
class TaskPlanner:
    def __init__(self, agent):
        self.agent = agent
        
    def plan(self, goal):
        """Decompose goal into executable steps"""
        # Analyze goal
        # Identify required tools
        # Create execution plan
        # Return ordered task list
        pass
    
    def execute_plan(self, plan):
        """Execute plan with milestone tracking"""
        # Execute steps in order
        # Track progress
        # Replan if obstacles arise
        pass
```

### 3. Multi-Agent Collaboration

**Concept**: Specialized agents for different tasks with collaboration patterns.

**Key Components**:
- Agent specialization by domain or capability
- Agent-to-agent communication protocols
- Task delegation and routing
- Conflict resolution mechanisms

**Refactoring Impact**: MEDIUM  
**Implementation Effort**: HIGH  
**Recommendation**: DEFER (implement after core improvements)

### 4. Long-Term Memory Systems

**Concept**: Persistent memory across sessions with retrieval mechanisms.

**Key Components**:
- Knowledge base for facts and concepts
- Preference learning from user interactions
- Entity tracking across sessions
- Semantic search for memory retrieval

**Refactoring Impact**: HIGH  
**Implementation Effort**: HIGH  
**Recommendation**: IMPLEMENT (after Phase 1)

### 5. Model Selection & Ensemble

**Concept**: Dynamic model selection based on task complexity.

**Key Components**:
- Task complexity assessment
- Model selection based on requirements
- Ensemble voting for critical decisions
- Cost optimization

**Refactoring Impact**: MEDIUM  
**Implementation Effort**: MEDIUM  
**Recommendation**: IMPLEMENT (after Phase 1)

---

## Implementation Phases

### Phase 1: Foundation Improvements (Week 1-2)
**Goal**: Implement high-impact, low-effort improvements

1. **Smart Tool Output Compression**
   - Implement LLM-based compression for tool outputs
   - Add importance scoring for tool results
   - Preserve critical information while reducing tokens

2. **Action Verification**
   - Add verification prompt for high-impact actions
   - Implement state tracking after action execution
   - Add rollback capability for failed actions

3. **Progress Tracking**
   - Add milestone tracking for long-running tasks
   - Implement progress reporting to user
   - Add checkpoint saving for resume capability

4. **Enhanced Error Recovery**
   - Implement retry with exponential backoff
   - Add error context preservation
   - Implement graceful degradation

### Phase 2: Memory & Planning (Week 3-4)
**Goal**: Add memory systems and planning capabilities

1. **Core Memory Blocks**
   - Implement typed JSON memory blocks
   - Add entity delta tracking
   - Implement memory injection on every call

2. **Task Planning**
   - Add planning layer before execution
   - Implement task decomposition
   - Add milestone tracking

3. **Long-Term Memory**
   - Implement knowledge base
   - Add preference learning
   - Implement semantic search

### Phase 3: Advanced Capabilities (Week 5-8)
**Goal**: Implement self-improvement and multi-agent patterns

1. **Self-Improvement**
   - Add code modification tools
   - Implement automated testing
   - Add version control integration

2. **Multi-Agent Patterns**
   - Implement agent specialization
   - Add agent-to-agent communication
   - Implement task delegation

3. **Model Selection**
   - Add task complexity assessment
   - Implement model selection
   - Add ensemble voting

---

## Known Issues & Technical Debt

### Issue 1: Streaming Tool Call Index Mismatch
**Symptom**: `APIError: Invalid diff: now finding less tool calls!`

**Root Cause**: Model predicts multiple tool calls in initial streaming tokens, then changes mind and reduces the number of tool calls.

**Current Mitigation**: Added tracking of tool call indices and automatic reset when mismatch is detected.

**Long-term Fix Needed**:
1. Implement model-level retry with adjusted prompts
2. Add tool call validation before streaming
3. Consider using non-streaming mode for tool calls
4. Implement graceful degradation when tool call prediction fails

**Reference**: Known limitation in OpenAI's streaming API when models change tool call predictions mid-stream.

### Issue 2: Context Management Complexity
**Symptom**: Five-layer context management is complex and hard to maintain

**Root Cause**: Each layer adds complexity without clear benefit

**Current State**: Layers L0-L4 with importance scoring

**Long-term Fix Needed**:
1. Simplify to three-layer approach
2. Add clear documentation for each layer
3. Implement automated testing for context management

### Issue 3: Limited Error Handling
**Symptom**: Tool failures cause session termination

**Root Cause**: No error recovery or retry mechanisms

**Current State**: Basic error handling exists but not comprehensive

**Long-term Fix Needed**:
1. Implement retry policy with exponential backoff
2. Add error context preservation
3. Implement graceful degradation

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