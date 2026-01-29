# OpenAI Prompt Engineering Resources

> Verified guides for GPT-5, Reasoning Models, and production-ready prompting techniques.

![Quality Score](https://img.shields.io/badge/Quality%20Score-9.29%2F10-brightgreen)
![Content](https://img.shields.io/badge/Content-2%20Guides%20EN%2BDE-blue)
![Verified](https://img.shields.io/badge/Verified-January%202026-blue)
![Sources](https://img.shields.io/badge/Sources-6%20Official%20OpenAI%20Docs-orange)

---

## Available Guides

| Guide | Language | Description |
|-------|----------|-------------|
| [prompt-engineering-en.md](./prompt-engineering-en.md) | English | Complete 2026 guide to GPT-5, Reasoning Models, and beyond |
| [prompt-engineering-de.md](./prompt-engineering-de.md) | Deutsch | Vollständiger 2026-Guide für GPT-5, Reasoning-Modelle und mehr |

---

## Evaluation Methodology

These guides were verified against **6 official OpenAI documentation sources** using a rigorous 6-point methodology:

### Quality Metrics

| Criterion | Score | Description |
|-----------|-------|-------------|
| **User Comprehension** | 8.75/10 | Clear structure, accessible language, logical progression |
| **Source Accuracy** | 8.5/10 | All quotes verified against original documentation |
| **Practical Applicability** | 10/10 | XML templates and code snippets directly usable |
| **Information Currency** | 10/10 | GPT-5.2, o3, o4-mini - all current as of January 2026 |
| **Practical Examples** | 9.5/10 | 12+ production-ready code snippets and templates |
| **Knowledge Extraction** | 9/10 | Novel insights for developers at all levels |

**Overall Score: 9.29/10**

### Verification Process

Each claim in the guides was cross-referenced against the original sources:

1. Direct quotes were matched word-for-word (English) or marked as translated (German)
2. Technical specifications were verified for accuracy
3. Code examples were checked for correct syntax
4. API parameters were validated against current documentation

---

## Sources Verified

All content was extracted and verified from these official OpenAI resources:

| # | Source | URL |
|---|--------|-----|
| 1 | Prompt Engineering Guide | https://platform.openai.com/docs/guides/prompt-engineering |
| 2 | Prompt Caching Guide | https://platform.openai.com/docs/guides/prompt-caching |
| 3 | Reasoning Best Practices | https://platform.openai.com/docs/guides/reasoning-best-practices |
| 4 | GPT-5 Prompting Guide | https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide |
| 5 | Prompt Optimizer | https://platform.openai.com/docs/guides/prompt-optimizer |
| 6 | Working with Evals | https://platform.openai.com/docs/guides/evals |

---

## Key Topics Covered

### Fundamentals
- What is Prompt Engineering?
- Model Selection (GPT vs Reasoning)
- Message Role Hierarchy (`developer` > `user` > `assistant`)
- The `instructions` API parameter
- Reusable Prompts with variables
- Structured Outputs

### Prompt Techniques
- Few-Shot Learning with examples
- RAG (Retrieval-Augmented Generation)
- Markdown + XML formatting

### API & Architecture
- Responses API vs Chat Completions
- Migration examples and performance impact

### Cost Optimization
- Prompt Caching (up to 90% cost savings)
- `prompt_cache_key` for improved hit rates
- Extended 24h retention for GPT-5.x
- Reasoning persistence for o3/o4-mini

### GPT-5 Specific
- Verbosity Control (`low`, `medium`, `high`)
- Agentic Eagerness tuning
- Tool Preambles for UX
- Self-Reflection Rubrics
- Frontend Code Editing Rules (XML templates)
- Coding Best Practices
- Cursor IDE Case Study

### Reasoning Models
- Reasoning Effort levels (`minimal` to `high`)
- Why NOT to use Chain-of-Thought
- `Formatting re-enabled` for Markdown output
- Visual Reasoning capabilities
- 7+ Customer Success Stories (Hebbia, Endex, Lindy.AI, etc.)

### Tooling
- Prompt Optimizer (Dashboard) with data preparation
- Evaluations (Evals) API with code examples
- Webhook monitoring
- Metaprompting techniques

---

## XML Templates

The guides contain XML-structured prompt templates from OpenAI's GPT-5 documentation:

- `<<context_gathering>>` - Control how the model gathers context
- `<persistence>` - Configure agentic autonomy
- `<<tool_preambles>>` - Improve UX during long tasks
- `<<self_reflection>>` - Enable quality self-evaluation
- `<<code_editing_rules>>` - Frontend development standards

See the full guides for complete templates with examples.

---

## Author

**Sabo Guenes**  
[cursorconsulting.org](https://cursorconsulting.org) | [LinkedIn](https://linkedin.com/in/sabriguenes)

---

*Last verified: January 2026*
