# OpenAI Prompt Engineering Guide

> The Complete 2026 Guide to Prompting GPT-5, Reasoning Models, and Beyond

*By Sabo Guenes | January 2026*

You've heard the buzz: "Prompting is the new programming." But what does that actually mean in practice? After diving deep into OpenAI's latest documentation and real-world case studies (including Cursor's integration of GPT-5), I've compiled everything you need to know.

---

## The Fundamentals

### What is Prompt Engineering?

> "Prompt engineering is the process of writing effective instructions for a model, such that it consistently generates content that meets your requirements."
> 
> — *OpenAI Documentation*[^1]

The key insight: prompting is **non-deterministic**. The same prompt can produce different outputs. Your goal is to maximize consistency while achieving quality.

### Model Selection Matters

OpenAI now offers two fundamentally different model families that require different prompting strategies:

| Model Type | Examples | Best For | Prompting Style |
|------------|----------|----------|-----------------|
| **Reasoning Models** | o3, o4-mini | Complex planning, ambiguous tasks | High-level goals, minimal detail |
| **GPT Models** | GPT-5, GPT-5.2, GPT-4.1 | Fast execution, well-defined tasks | Explicit, detailed instructions |

> "You could think about the difference between reasoning and GPT models like this: A reasoning model is like a senior co-worker. You can give them a goal to achieve and trust them to work out the details. A GPT model is like a junior coworker. They'll perform best with explicit instructions."
> 
> — *OpenAI Reasoning Best Practices*[^2]

---

## Prompt Caching: Save 90% on Costs

One of the most underutilized features. If you're not using prompt caching, you're overpaying.

### The Numbers

| Metric | Savings |
|--------|---------|
| **Latency** | Up to 80% reduction |
| **Input Token Costs** | Up to 90% reduction |

> "Prompt Caching can reduce latency by up to 80% and input token costs by up to 90%."
> 
> — *OpenAI Prompt Caching Guide*[^3]

### How It Works

1. Caching is **automatic** for prompts ≥1024 tokens
2. Works on **exact prefix matches**
3. Cache typically persists 5-10 minutes (in-memory) or up to 24 hours (extended)

### The Golden Rule

```
┌─────────────────────────────────────────┐
│  STATIC CONTENT (system prompt, etc.)  │  ← Put this FIRST
├─────────────────────────────────────────┤
│  DYNAMIC CONTENT (user input, etc.)    │  ← Put this LAST
└─────────────────────────────────────────┘
```

> "Place static content like instructions and examples at the beginning of your prompt, and put variable content, such as user-specific information, at the end."
> 
> — *OpenAI Prompt Caching Guide*[^3]

### Extended Retention (24h)

Available for GPT-5.x models:

```json
{
  "model": "gpt-5.1",
  "input": "Your prompt goes here...",
  "prompt_cache_retention": "24h"
}
```

---

## Message Roles: The Chain of Command

OpenAI models follow a **hierarchy of trust**:

| Role | Priority | Purpose |
|------|----------|---------|
| `developer` | Highest | System rules, business logic |
| `user` | Medium | End-user inputs |
| `assistant` | - | Model-generated responses |

> "Developer messages are instructions provided by the application developer, prioritized ahead of user messages."
> 
> — *OpenAI Prompt Engineering Guide*[^1]

### Practical Example

```javascript
const response = await client.responses.create({
  model: "gpt-5",
  input: [
    { role: "developer", content: "Talk like a pirate." },  // Priority 1
    { role: "user", content: "Are semicolons optional in JavaScript?" }  // Priority 2
  ],
});
```

---

## Formatting: Markdown + XML

Structure your prompts with clear sections:

```markdown
# Identity
You are a coding assistant that...

# Instructions
* When defining variables, use snake_case
* Do not give responses with Markdown formatting

# Examples
<<user_query>>
How do I declare a string variable?
<</user_query>>

<<assistant_response>>
var first_name = "Anna";
<</assistant_response>>
```

> "Markdown headers and lists can be helpful to mark distinct sections of a prompt, and to communicate hierarchy to the model."
> 
> — *OpenAI Prompt Engineering Guide*[^1]

---

## GPT-5 Specific Best Practices

GPT-5 is OpenAI's most steerable model yet. Here's how to get the most out of it.

### Controlling Agentic Eagerness

GPT-5 can be configured anywhere from "ask before every action" to "complete autonomy."

#### For Less Eagerness (Faster, Cheaper)

```xml
<<context_gathering>>
Goal: Get enough context fast. Parallelize discovery and stop as soon as you can act.
Method:
- Start broad, then fan out to focused subqueries.
- Avoid over searching for context.
Early stop criteria:
- You can name exact content to change.
- Top hits converge (~70%) on one area/path.
<</context_gathering>>
```

> — *OpenAI GPT-5 Prompting Guide*[^4]

#### For More Eagerness (Full Autonomy)

```xml
<persistence>
- You are an agent - please keep going until the user's query is completely resolved
- Only terminate your turn when you are sure that the problem is solved
- Never stop or hand back to the user when you encounter uncertainty
- Do not ask the human to confirm or clarify assumptions
</persistence>
```

> — *OpenAI GPT-5 Prompting Guide*[^4]

### Tool Preambles

For better user experience during long-running tasks:

```xml
<<tool_preambles>>
- Always begin by rephrasing the user's goal in a friendly, clear manner
- Outline a structured plan detailing each logical step
- Narrate each step succinctly and sequentially
- Finish by summarizing completed work
<</tool_preambles>>
```

> — *OpenAI GPT-5 Prompting Guide*[^4]

### Self-Reflection Rubrics

For zero-to-one app generation:

```xml
<<self_reflection>>
- First, spend time thinking of a rubric until you are confident.
- Create a rubric with 5-7 categories. This is for your purposes only.
- Use the rubric to iterate on the best possible solution.
- If not hitting top marks across all categories, start again.
<</self_reflection>>
```

> — *OpenAI GPT-5 Prompting Guide*[^4]

---

## Case Study: Cursor's GPT-5 Integration

Cursor (the AI code editor) was an alpha tester for GPT-5. Their learnings are invaluable.

### Problem: Verbose Outputs

GPT-5 was producing too many status updates that disrupted user flow.

### Solution: Dual Verbosity Control

1. Set API `verbosity` parameter to `low` globally
2. Add prompt instruction for verbose **code only**:

```
Write code for clarity first. Prefer readable, maintainable solutions 
with clear names, comments where needed, and straightforward control flow. 
Use high verbosity for writing code and code tools.
```

> — *Cursor Team, via OpenAI GPT-5 Prompting Guide*[^4]

### Problem: Too Many Clarifying Questions

GPT-5 was deferring to users unnecessarily.

### Solution: Explicit Autonomy Instructions

```
Be aware that the code edits you make will be displayed to the user as 
proposed changes, which means (a) your code edits can be quite proactive, 
as the user can always reject, and (b) your code should be well-written 
and easy to quickly review.

If proposing next steps that would involve changing the code, make those 
changes proactively for the user to approve/reject rather than asking 
whether to proceed.
```

> — *Cursor Team, via OpenAI GPT-5 Prompting Guide*[^4]

### Warning: Contradictory Instructions

> "GPT-5's careful instruction-following behavior means that poorly-constructed prompts containing contradictory or vague instructions can be more damaging to GPT-5 than to other models, as it expends reasoning tokens searching for a way to reconcile the contradictions."
> 
> — *OpenAI GPT-5 Prompting Guide*[^4]

**Review your prompts for conflicts before deploying!**

---

## Reasoning Models: Different Rules Apply

For o3, o4-mini, and other reasoning models, **forget everything you know about Chain-of-Thought prompting**.

### DON'T Do This

```
❌ "Think step by step"
❌ "Explain your reasoning"
❌ "Show your work"
```

> "Since these models perform reasoning internally, prompting them to 'think step by step' or 'explain your reasoning' is unnecessary."
> 
> — *OpenAI Reasoning Best Practices*[^2]

### DO This Instead

- Keep prompts **simple and direct**
- Try **zero-shot first** (no examples)
- Use delimiters (XML, Markdown) for structure
- Be specific about constraints

### When to Use Reasoning Models

| Use Case | Why It Works |
|----------|--------------|
| **Navigating ambiguity** | Understands intent from limited info |
| **Needle in haystack** | Finds relevant info in massive datasets |
| **Complex documents** | Legal contracts, financial statements |
| **Agentic planning** | Multi-step strategy development |
| **Visual reasoning** | Complex charts, architectural drawings |
| **Code review** | Catches subtle bugs |
| **LLM-as-Judge** | Evaluating other model outputs |

> "We swapped GPT-4o for o1 and found that o1 was much better at reasoning over the interplay between documents to reach logical conclusions that were not evident in any one single document. As a result, we saw a 4x improvement in end-to-end performance."
> 
> — *Blue J (tax research platform), via OpenAI*[^2]

---

## Frontend Development Stack

For GPT-5 frontend projects, OpenAI recommends:

| Category | Recommended |
|----------|-------------|
| **Framework** | Next.js (TypeScript), React |
| **Styling** | Tailwind CSS, shadcn/ui, Radix Themes |
| **Icons** | Material Symbols, Heroicons, Lucide |
| **Animation** | Motion |
| **Fonts** | Inter, Geist, Mona Sans |

> — *OpenAI GPT-5 Prompting Guide*[^4]

---

## Tooling: Prompt Optimizer & Evals

### Prompt Optimizer

OpenAI's dashboard tool for automatic prompt improvement:

1. Create a dataset with prompt + evaluation data
2. Add annotations (Good/Bad) + critiques
3. Click "Optimize" → new improved version

> "The prompt optimizer is a chat interface in the dashboard, where you enter a prompt, and we optimize it according to current best practices."
> 
> — *OpenAI Prompt Optimizer Guide*[^5]

### Evaluations (Evals)

Test your prompts systematically:

1. Define success criteria (graders)
2. Create test datasets
3. Run evals on prompt changes
4. Iterate based on results

> "Evaluations test model outputs to ensure they meet style and content criteria that you specify. Writing evals is an essential component to building reliable applications."
> 
> — *OpenAI Evals Guide*[^6]

---

## Practical Recommendations

### 1. Pin Model Versions

```javascript
model: "gpt-4.1-2025-04-14"  // ✅ Specific snapshot
model: "gpt-4.1"             // ⚠️ May change behavior over time
```

### 2. Build Evals Early

Don't wait until production to discover your prompt fails edge cases.

### 3. Use Reusable Prompts

Store prompts in OpenAI's dashboard with versioning:

```javascript
prompt: {
  id: "pmpt_abc123",
  version: "2",
  variables: { customer_name: "Jane Doe" }
}
```

### 4. Monitor Cached Token Usage

Check `usage.prompt_tokens_details.cached_tokens` to verify caching is working.

### 5. Use Metaprompting

Ask GPT-5 to improve its own prompts:

```
Here's a prompt: [PROMPT]
The desired behavior is [X], but instead it [Y]. 
What minimal edits would you make to consistently elicit the desired behavior?
```

> — *OpenAI GPT-5 Prompting Guide*[^4]

---

## References

[^1]: OpenAI. "Prompt Engineering." *OpenAI Platform Documentation*, January 2026. https://platform.openai.com/docs/guides/prompt-engineering

[^2]: OpenAI. "Reasoning Best Practices." *OpenAI Platform Documentation*, January 2026. https://platform.openai.com/docs/guides/reasoning-best-practices

[^3]: OpenAI. "Prompt Caching." *OpenAI Platform Documentation*, January 2026. https://platform.openai.com/docs/guides/prompt-caching

[^4]: OpenAI. "GPT-5 Prompting Guide." *OpenAI Cookbook*, August 2025. https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide

[^5]: OpenAI. "Prompt Optimizer." *OpenAI Platform Documentation*, January 2026. https://platform.openai.com/docs/guides/prompt-optimizer

[^6]: OpenAI. "Working with Evals." *OpenAI Platform Documentation*, January 2026. https://platform.openai.com/docs/guides/evals

---

*Have questions? Contact me at [cursorconsulting.org](https://cursorconsulting.org)*
