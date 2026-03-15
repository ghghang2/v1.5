# Related Research on Self-Improving Agents (2024-2026)

This document compiles research on autonomous self-improving agents, recursive self-improvement, and meta-agent frameworks published since 2024.

**Last Updated:** 2026-03-15

---

## Table of Contents

1. [ADAS: Automated Design of Agentic Systems](#adas-automated-design-of-agentic-systems)
2. [Recursive Introspection (RISE)](#recursive-introspection-rise)
3. [Meta-Agent Teams](#meta-agent-teams)
4. [AI with Recursive Self-Improvement (ICLR 2026)](#ai-with-recursive-selfimprovement-iclr-2026)
5. [Comparative Analysis](#comparative-analysis)
6. [References](#references)

---

## 1. ADAS: Automated Design of Agentic Systems

### Publication Details
- **Title:** Automated Design of Agentic Systems
- **Authors:** Shengran Hu, Cong Lu, Jeff Clune
- **Venue:** ICLR 2025, NeurIPS 2024 Open-World Agent Workshop (Outstanding Paper)
- **arXiv:** 2408.08435 [cs.AI]
- **Last Revised:** 2 Mar 2025 (v2)
- **Website:** https://www.shengranhu.com/ADAS/
- **Code:** https://github.com/ShengranHu/ADAS

### Abstract Summary
> "Researchers are investing substantial effort in developing powerful general-purpose agents, wherein Foundation Models are used as modules within agentic systems (e.g. Chain-of-Thought, Self-Reflection, Toolformer). However, the history of machine learning teaches us that hand-designed solutions are eventually replaced by learned solutions. We describe a newly forming research area, Automated Design of Agentic Systems (ADAS), which aims to automatically create powerful agentic system designs..."

### Core Contribution
ADAS proposes an algorithm called **Meta Agent Search** where a "meta" agent iteratively programs new agents in code based on previous discoveries. Given that programming languages are Turing Complete, this approach theoretically enables learning any possible agentic system.

### Algorithm: Meta Agent Search
```
1. Meta Agent programs new agent designs in code
2. Tests performance on tasks
3. Adds successful agents to archive
4. Uses archive to inform subsequent iterations
```

### Implementation Details (from https://www.shengranhu.com/ADAS/)

#### Structure
```
ADAS/
├── _arc/           # ARC-AGI dataset
├── _drop/          # DROP reading comprehension
├── _gpqa/          # GPQA graduate-level QA
├── _mgsm/          # MGSM math
├── _mmlu/          # MMLU multitask
├── _transfer_math/ # Transfer math tasks
├── dataset/        # Datasets
├── misc/           # Miscellaneous
├── results/        # Results
├── README.md
├── requirements.txt
└── search.py       # Main search algorithm
```

#### Key Python Module: FM_Module
The code demonstrates a Forward Module (FM_Module) pattern:
```python
def forward(self, taskInfo):
    # Step 1: Generate initial candidates
    initial_instruction = 'Please think step by step and then solve...'
    num_candidates = 5
    initial_module = [FM_Module(['thinking', 'code'], 'Initial Solution', temperature=0.8) 
                     for _ in range(num_candidates)]
    
    # Step 2: Human-like feedback
    human_like_feedback_module = FM_Module(['thinking', 'feedback'], 'Human-like Feedback')
    
    # Step 3: Expert advisors
    expert_roles = ['Efficiency Expert', 'Readability Expert', 'Simplicity Expert']
    expert_advisors = [FM_Module(['thinking', 'feedback'], role, temperature=0.6) 
                      for role in expert_roles]
    
    # Step 4: Refinement
    max_refinement_iterations = 3
    refinement_module = FM_Module(['thinking', 'code'], 'Refinement Module')
    
    # Step 5: Final decision using ensemble
    final_decision_module = FM_Module(['thinking', 'code'], 'Final Decision', temperature=0.1)
```

#### Discovered Agent Examples
The paper reports several novel agent architectures discovered by Meta Agent Search:

1. **ARC-AGI Agent** - Uses Physics/Chemistry/Biology experts with critics
2. **Science QA Agent** - Problem decomposition + specialized experts
3. **DROP Agent** - Multi-hop reasoning with feedback loop

### Experimental Results
- **Domains tested:** ARC-AGI, DROP, MGSM, MMLU, GPQA
- **Performance:** Discovered agents outperform hand-designed baselines
- **Transferability:** Maintains performance across domains and models
- **Novelty:** Agents invent new architectural patterns not seen in literature

### Safety Considerations
> "The code in this repository involves executing untrusted model-generated code. We strongly advise users to be aware of this safety concern."

---

## 2. Recursive Introspection (RISE)

### Publication Details
- **Title:** Recursive Introspection: Teaching Language Model Agents How to Self-Improve
- **Authors:** Yifan Qu, Tianyi Zhang, Neel Garg, Aviral Kumar
- **Venue:** NeurIPS 2024 (Advances in Neural Information Processing Systems)
- **arXiv:** 2406.04217
- **Citations:** 164+ (as of 2026)
- **Related Workshop:** ICML 2024 Workshop on Self-Improving Agents

### Abstract Summary (from Google Scholar)
> "Our key insight is to supervise improvements to the learner's own responses in an iterative fashion. In this paper, we develop RISE: Recursive Introspection, that utilizes these insights to improve the self-improvement ability of an LLM."

### Core Idea
RISE teaches LLM agents to recursively detect and correct their previous mistakes through self-improvement cycles. Unlike Gödel Agent which modifies its own code, RISE focuses on iterative response improvement.

### Key Features
1. **Self-Reflection:** Agent analyzes its own previous responses
2. **Iterative Correction:** Multiple passes of improvement
3. **Supervised Learning:** External supervision guides self-improvement
4. **Sequential Processing:** Improvements built incrementally

### Citation
```
@article{qu2024recursiveintrospection,
  title={Recursive Introspection: Teaching language model agents how to self-improve},
  author={Qu, Yifan and Zhang, Tianyi and Garg, Neel and Kumar, Aviral},
  journal={Advances in Neural Information Processing Systems},
  year={2024}
}
```

### Related Work Connection
RISE complements Gödel Agent by:
- Focusing on **response-level** improvement vs. **code-level** modification
- Using external supervision vs. autonomous evolution
- Iterative refinement vs. recursive self-update

---

## 3. Meta-Agent Teams

### Repository
- **URL:** https://github.com/jbrahy/meta-agent-teams
- **License:** AGPL-3.0
- **Last Updated:** Mar 14, 2026
- **Stars:** 1 (as of review)

### Description
> "An open framework for building self-improving AI agent teams. Includes a meta-agent architecture with independent auditing, git-backed evolution, and structured feedback loops."

### Architecture Diagram
```
┌─────────────────────┐
│ Human (You)         │  Execute, evaluate, provide feedback
└─────────┬───────────┘
          │ feedback, review, audits
          ▼
┌─────────────────────┐    ┌──────────────────────┐
│ Meta-Agent          │◄───┤ Auditor Agent        │
│ Evolves agents      │    │ Checks for:          │
│ based on feedback   │    │ - drift, bias,       │
└─────────┬───────────┘    │ - regression         │
          │
          ▼
┌─────────────────────┐
│ Your Agent Team     │  Specialists that advise
│ - Marketing (8)     │  - you decide & execute
│ - Custom builds     │
└─────────────────────┘
```

### Key Components

1. **Meta-Agent:** Processes feedback and evolves agent designs
2. **Auditor Agent:** Independent reviewer that prevents drift and bias
3. **Agent Team:** Collection of specialist agents
4. **Git-backed Evolution:** Full history of all changes with rationale

### Structure
```
meta-agent-teams/
├── teams/
│   └── marketing/
│       ├── agents/      # SDR, content, analytics, SEO, etc.
│       ├── meta-agent/  # Feedback processor and agent evolver
│       ├── auditor/     # Independent reviewer
│       ├── shared/      # Constitution and glossary
│       ├── feedback/    # Structured feedback templates
│       └── evals/       # Performance tracking
├── skill/               # Team-builder skill for Claude Code
├── prompt/
│   └── agent-team-builder.md  # Portable prompt
└── docs/
    ├── architecture.md
    ├── getting-started.md
    └── domain-guide.md
```

### Key Differentiators

| Feature | Gödel Agent | RISE | Meta-Agent Teams |
|---------|-------------|------|------------------|
| **Self-Improvement Level** | Code-level (monkey patching) | Response-level | Team-level |
| **Autonomy** | Fully autonomous | Supervised | Human-guided |
| **Safety** | Restricted modifications | External supervision | Independent auditor |
| **Persistence** | Runtime memory | Session-based | Git-backed |
| **Multi-Agent** | Single agent | Single agent | Team architecture |

---

## 4. AI with Recursive Self-Improvement (ICLR 2026)

### Publication Details
- **Title:** AI with Recursive Self-Improvement
- **Venue:** ICLR 2026 Workshop
- **Link:** https://openreview.net/forum?id=...
- **Authors:** (Research community effort)

### Context
This workshop focuses on exploring risks and opportunities in self-improving AI agents. Key topics include:
- Known risks in self-improving agents
- Testbeds for continual adaptation
- Safety frameworks for autonomous improvement

### Related Themes
- **Continual Adaptation:** Agents adapting to evolving environments
- **Safety Concerns:** Preventing destructive self-modification
- **Alignment:** Maintaining original objectives during improvement

---

## 5. Comparative Analysis

### Comparison with Gödel Agent

| Aspect | Gödel Agent | ADAS (Meta Agent Search) | RISE | Meta-Agent Teams |
|--------|-------------|-------------------------|------|------------------|
| **Improvement Mechanism** | Monkey patching | Code programming | Iterative correction | Team evolution |
| **Self-Reference** | Full (read/write own code) | Partial (programs agents) | Limited (reflection) | Medium (auditor) |
| **Search Space** | Full design space | Novel architectures | Response space | Team configurations |
| **Human Priors** | Minimal | Some (task setup) | Significant (supervision) | High (team design) |
| **Persistence** | Runtime | Archive-based | Session | Git history |
| **Safety** | Critical function restrictions | Code execution risks | External supervision | Independent auditor |
| **Autonomy Level** | Highest | High | Medium | Low-Medium |

### Complementarity Analysis

1. **Gödel Agent + ADAS:** 
   - Gödel's recursive self-update could be enhanced by ADAS's diverse agent design patterns
   - ADAS's Meta Agent Search could be implemented within Gödel's framework

2. **Gödel Agent + RISE:**
   - RISE's self-reflection could be integrated as an additional action
   - Could improve the quality of self-modification decisions

3. **Gödel Agent + Meta-Agent Teams:**
   - Meta-Agent Teams' auditor could provide safety checks for Gödel's modifications
   - Git-backed persistence could replace runtime-only state

4. **Combined Framework:**
```
┌─────────────────────────────────────────────────────────┐
│                    Enhanced Self-Improving Agent        │
├─────────────────────────────────────────────────────────┤
│  Gödel Core:                                            │
│  - Self-awareness (action_environment_aware)           │
│  - Code reading (action_read_logic)                    │
│  - Code modification (action_adjust_logic)             │
│                                                         │
│  + ADAS Components:                                     │
│  - Meta Agent Search for design patterns               │
│  - FM_Module pattern for building blocks               │
│                                                         │
│  + RISE Components:                                     │
│  - Recursive introspection for quality checking        │
│  - Iterative refinement before committing              │
│                                                         │
│  + Safety:                                              │
│  - Auditor agent for change validation                 │
│  - Git-backed version control                          │
│  - Restricted function list (like Gödel)               │
└─────────────────────────────────────────────────────────┘
```

---

## 6. References

1. **Gödel Agent:**
   - Yin, X., Wang, X., Pan, L., et al. "Gödel Agent: A Self-Referential Agent Framework for Recursive Self-Improvement." arXiv:2410.04444, Oct 2024.
   - https://arxiv.org/abs/2410.04444
   - https://github.com/Arvid-pku/Godel_Agent

2. **ADAS:**
   - Hu, S., Lu, C., Clune, J. "Automated Design of Agentic Systems." arXiv:2408.08435, Aug 2024.
   - https://arxiv.org/abs/2408.08435
   - https://github.com/ShengranHu/ADAS

3. **RISE:**
   - Qu, Y., Zhang, T., Garg, N., Kumar, A. "Recursive Introspection: Teaching Language Model Agents How to Self-Improve." NeurIPS 2024.
   - https://arxiv.org/abs/2406.04217

4. **Meta-Agent Teams:**
   - https://github.com/jbrahy/meta-agent-teams

5. **ICLR 2026 Workshop:**
   - "AI with Recursive Self-Improvement" Workshop. OpenReview.net.
   - https://openreview.net/

6. **Growing Recursive Self-Improvers:**
   - Steunebrink, B.R., Thorisson, K.R. "Growing Recursive Self-Improvers." Conference on Artificial Intelligence, 2016.
   - Springer.

7. **Bounded Recursive Self-Improvement:**
   - Nivel, E., Thorisson, K.R., Steunebrink, B.R. "Bounded Recursive Self-Improvement." arXiv preprint, 2013.

---

## Appendix A: Key Research Trends (2024-2026)

1. **Shift from Hand-Designed to Learned Agents:**
   - All major frameworks move away from fixed architectures
   - Emphasis on discovering novel designs autonomously

2. **Multi-Agent Collaboration:**
   - Moving from single agents to teams with specialized roles
   - Auditor/Reviewer patterns for safety

3. **Safety-First Approach:**
   - Git-backed evolution for auditability
   - Independent verification mechanisms
   - Restricted modification scopes

4. **Transferability as Key Metric:**
   - Performance across domains matters more than single-task optimization
   - Robustness to model changes is essential

5. **Code as First-Class Citizen:**
   - Programming languages enable Turing-complete agent design
   - Code persistence (git, file-based) for reproducibility

---

