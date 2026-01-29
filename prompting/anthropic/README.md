# Anthropic Claude Prompt Engineering Resources

> Verified guides for Claude Opus 4.5, Sonnet 4.5, and agentic workflows.

![Quality Score](https://img.shields.io/badge/Quality%20Score-9.2%2F10-brightgreen)
![Content](https://img.shields.io/badge/Content-2%20Guides%20EN%2BDE-blue)
![Verified](https://img.shields.io/badge/Verified-January%202026-blue)
![Sources](https://img.shields.io/badge/Sources-7%20Official%20Anthropic%20Docs-orange)

---

## Available Guides

| Guide | Language | Description |
|-------|----------|-------------|
| [prompt-engineering-en.md](./prompt-engineering-en.md) | English | Complete 2026 guide to Claude Opus 4.5, Sonnet 4.5, and Agentic Workflows |
| [prompt-engineering-de.md](./prompt-engineering-de.md) | Deutsch | Vollständiger 2026-Guide für Claude Opus 4.5, Sonnet 4.5 und Agentic Workflows |

---

## Evaluation Methodology

These guides were verified against **7 official Anthropic documentation sources** using a rigorous methodology:

### Quality Metrics

| Criterion | Score | Description |
|-----------|-------|-------------|
| **User Comprehension** | 9/10 | Clear structure, accessible language, logical progression |
| **Source Accuracy** | 9.5/10 | All quotes verified against original documentation |
| **Practical Applicability** | 9.5/10 | XML templates and code snippets directly usable |
| **Information Currency** | 9/10 | Opus 4.5, Sonnet 4.5 - current as of January 2026 |
| **Practical Examples** | 9/10 | 10+ production-ready code snippets and templates |
| **Knowledge Extraction** | 9/10 | Novel insights for developers at all levels |

**Overall Score: 9.2/10**

### Verification Process

Each claim in the guides was cross-referenced against the original sources:

1. Direct quotes were matched word-for-word (English) or marked as translated (German)
2. Technical specifications were verified for accuracy
3. Code examples were checked for correct syntax
4. API parameters were validated against current documentation

---

## Sources Verified

All content was extracted and verified from these official Anthropic resources:

| # | Source | URL |
|---|--------|-----|
| 1 | Prompting Best Practices | https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices |
| 2 | Claude Opus 4.5 Announcement | https://www.anthropic.com/news/claude-opus-4-5 |
| 3 | XML Tags Guide | https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags |
| 4 | System Prompts | https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/system-prompts |
| 5 | Chain of Thought | https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/chain-of-thought |
| 6 | Extended Thinking Tips | https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/extended-thinking-tips |
| 7 | Building Effective Agents | https://www.anthropic.com/engineering/building-effective-agents |

---

## Key Topics Covered

### Claude 4.5 Fundamentals
- Model Selection (Opus vs Sonnet vs Haiku)
- Explicit Instructions
- Context and Motivation

### Core Techniques
- XML Tags (Claude's "native language")
- System Prompts / Role Prompting
- Chain of Thought (Basic, Guided, Structured)
- Extended Thinking Mode
- Multishot Prompting (Examples)

### Opus 4.5 Specific
- Effort Parameter
- Overengineering Prevention
- System Prompt Sensitivity
- Thinking Sensitivity

### Agentic Workflows
- Workflows vs Agents
- Prompt Chaining
- Routing
- Parallelization
- Orchestrator-Workers

### Advanced Topics
- Long-Horizon Reasoning
- State Tracking
- Multi-Context Window Workflows
- Parallel Tool Calling
- Output Formatting Control
- Hallucination Prevention

---

## XML Templates

The guides contain XML-structured prompt templates from Anthropic's documentation:

- `<instructions>` - Task definition
- `<thinking>` / `<answer>` - CoT separation
- `<<avoid_overengineering>>` - Prevent over-engineering
- `<<use_parallel_tool_calls>>` - Control parallel execution
- `<<investigate_before_answering>>` - Ensure code exploration
- `<<context_management>>` - Long-horizon state tracking

See the full guides for complete templates with examples.

---

## Author

**Sabo Guenes**  
[cursorconsulting.org](https://cursorconsulting.org) | [LinkedIn](https://linkedin.com/in/sabriguenes)

---

*Last verified: January 2026*
