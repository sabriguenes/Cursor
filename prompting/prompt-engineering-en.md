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

### What Can Be Cached

The following content types contribute to the 1024 token minimum:

| Content Type | Notes |
|--------------|-------|
| **Messages** | Complete messages array (developer, user, assistant) |
| **Images** | Links or base64-encoded, including multiple images |
| **Tool definitions** | The list of available `tools` |
| **Structured output schema** | Serves as a prefix to the system message |

> — *OpenAI Prompt Caching Guide*[^3]

### Improve Cache Hit Rates

Use the `prompt_cache_key` parameter to influence routing and improve cache hit rates:

```json
{
  "model": "gpt-5.1",
  "input": "Your prompt goes here...",
  "prompt_cache_key": "my-app-v1"
}
```

> "Requests are routed to a machine based on a hash of the initial prefix of the prompt. The hash typically uses the first 256 tokens... If requests for the same prefix and `prompt_cache_key` combination exceed ~15 requests per minute, some may overflow and get routed to additional machines, reducing cache effectiveness."
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

> **Note:** Extended caching is NOT compatible with Zero Data Retention (ZDR). In-memory caching is ZDR-compatible.

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

### The `instructions` Parameter

The Responses API offers an `instructions` parameter for high-level guidance:

```javascript
const response = await client.responses.create({
  model: "gpt-5",
  instructions: "Talk like a pirate.",  // High-priority instructions
  input: "Are semicolons optional in JavaScript?",
});
```

> "The `instructions` parameter gives the model high-level instructions on how it should behave while generating a response... Any instructions provided this way will take priority over a prompt in the `input` parameter."
> 
> — *OpenAI Prompt Engineering Guide*[^1]

**Note:** The `instructions` parameter only applies to the current request. It is not persisted when using `previous_response_id`.

### Using Message Roles

Alternatively, use the `input` array with explicit roles:

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

## Reusable Prompts (Dashboard)

OpenAI's dashboard allows you to create reusable prompts with variables:

```javascript
const response = await client.responses.create({
  model: "gpt-5",
  prompt: {
    id: "pmpt_abc123",
    version: "2",
    variables: {
      customer_name: "Jane Doe",
      product: "40oz juice box"
    }
  }
});
```

Variables can also include file inputs for document-based prompts:

```javascript
variables: {
  topic: "Dragons",
  reference_pdf: {
    type: "input_file",
    file_id: "file-abc123"  // Previously uploaded file
  }
}
```

> — *OpenAI Prompt Engineering Guide*[^1]

---

## Structured Outputs

For applications requiring JSON responses, use **Structured Outputs** to ensure the model returns data conforming to a JSON schema:

```javascript
const response = await client.responses.create({
  model: "gpt-5",
  input: "Extract the name and age from: John is 25 years old.",
  text: {
    format: {
      type: "json_schema",
      json_schema: {
        name: "person",
        schema: {
          type: "object",
          properties: {
            name: { type: "string" },
            age: { type: "integer" }
          },
          required: ["name", "age"]
        }
      }
    }
  }
});
```

> "In addition to plain text, you can also have the model return structured data in JSON format - this feature is called Structured Outputs."
> 
> — *OpenAI Prompt Engineering Guide*[^1]

---

## Few-Shot Learning

Few-shot learning lets you steer a model toward a new task by including a handful of input/output examples in the prompt. The model implicitly "picks up" the pattern from those examples and applies it to new inputs.

### When to Use Few-Shot

- Classification tasks (sentiment, category, priority)
- Formatting requirements (specific output structure)
- Domain-specific terminology
- Edge case handling

### Example: IT Ticket Categorization

```markdown
# Instructions
Categorize the following support ticket into one of: Hardware, Software, or Other.
Respond with only one of those words.

# Examples
<<ticket id="example-1">>
My monitor won't turn on after I moved desks. The power light stays off.
<</ticket>>

<<assistant_response id="example-1">>
Hardware
<</assistant_response>>

<<ticket id="example-2">>
I updated the app and now it crashes on launch with an error code 0x0004.
<</ticket>>

<<assistant_response id="example-2">>
Software
<</assistant_response>>

<<ticket id="example-3">>
What are the best restaurants in Cleveland for a team dinner?
<</ticket>>

<<assistant_response id="example-3">>
Other
<</assistant_response>>
```

> **Tip:** When providing examples, show a diverse range of possible inputs with the desired outputs. Try to cover edge cases.

---

## Retrieval-Augmented Generation (RAG)

RAG is the technique of adding relevant context information to your prompt that the model can use to generate a response.

### Why Use RAG?

- Give the model access to **proprietary data** outside its training set
- Constrain responses to **specific sources** you trust
- Keep responses **up-to-date** with current information

### How to Implement

1. **Query your knowledge base** (vector database, file search, etc.)
2. **Include retrieved context** in the prompt
3. **Reference the context** in your instructions

```markdown
# Instructions
Answer the user's question based ONLY on the provided context.
If the answer is not in the context, say "I don't have that information."

# Context
<<document source="internal-wiki">>
Our refund policy allows returns within 30 days of purchase.
Items must be unopened and in original packaging.
Digital products are non-refundable.
<</document>>

# User Question
Can I return a software license I bought last week?
```

### Practical Tips

- Put retrieved context **before** the user question.
- Keep context **short and relevant** (remove noise).
- If you need traceability, include **citations** (doc IDs, URLs, or quoted snippets) in the context and require the model to reference them.

---

## Responses API vs Chat Completions

OpenAI offers two APIs for text generation. For GPT-5, the **Responses API** is strongly recommended.

### Key Differences

| Feature | Responses API | Chat Completions |
|---------|---------------|------------------|
| **Reasoning Persistence** | Reasoning items preserved between turns | Stateless, no persistence |
| **Agentic Performance** | Optimized for multi-turn tool calling | Basic tool support |
| **Previous Context** | Use `previous_response_id` | Manual message management |
| **Recommended For** | GPT-5, agentic workflows | Legacy applications |

### Performance Impact

> "We observed Tau-Bench Retail score increases from 73.9% to 78.2% just by switching to the Responses API and including `previous_response_id`."
> 
> — *OpenAI GPT-5 Prompting Guide*[^4]

### Migration Example

**Chat Completions (Old):**
```javascript
const response = await client.chat.completions.create({
  model: "gpt-5",
  messages: [
    { role: "system", content: "You are a helpful assistant." },
    { role: "user", content: "Hello!" }
  ]
});
```

**Responses API (New):**
```javascript
const response = await client.responses.create({
  model: "gpt-5",
  input: [
    { role: "developer", content: "You are a helpful assistant." },
    { role: "user", content: "Hello!" }
  ]
});
```

---

## GPT-5 Specific Best Practices

GPT-5 is OpenAI's most steerable model yet. Here's how to get the most out of it.

### Coding Best Practices

For coding tasks with GPT-5, focus on these areas:

| Area | Recommendation |
|------|----------------|
| **Role Definition** | Frame the model as a software engineering agent with clear responsibilities |
| **Testing** | Instruct to test changes with unit tests; validate patches carefully |
| **Tool Examples** | Include concrete examples of how to invoke commands |
| **Markdown** | Generate clean, semantically correct markdown with backticks for code |

> "Prompting GPT-5 for coding tasks is most effective when following a few best practices: define the agent's role, enforce structured tool use with examples, require thorough testing for correctness, and set Markdown standards for clean output."
> 
> — *OpenAI Prompt Engineering Guide*[^1]

### Verbosity Control

GPT-5 introduces a new `verbosity` API parameter that controls the length of final answers (not reasoning):

| Value | Effect |
|-------|--------|
| `low` | Concise responses, minimal explanations |
| `medium` | Balanced (default) |
| `high` | Detailed explanations and context |

You can override this globally set parameter with natural-language instructions in specific contexts. For example: set `verbosity: "low"` globally, but add "Use high verbosity for code" in your prompt.

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

### Reasoning Effort Levels

The `reasoning_effort` parameter controls how hard the model thinks:

| Level | Use Case | Trade-off |
|-------|----------|-----------|
| `minimal` | Latency-sensitive, simple tasks | Fastest, benefits from GPT-4.1 prompting patterns |
| `low` | Quick decisions | Fast with some reasoning |
| `medium` | Default, balanced | Good for most tasks |
| `high` | Complex multi-step tasks | Most thorough, higher latency |

> **Tip:** For `minimal` reasoning, prompt the model to give a brief explanation at the start of the final answer (e.g., bullet points) to improve performance.

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

### Enable Markdown Output

By default, reasoning models avoid Markdown formatting in API responses. To enable it:

```
Formatting re-enabled

You are an assistant that helps with code review...
```

> "Starting with `o1-2024-12-17`, reasoning models in the API will avoid generating responses with markdown formatting. To signal to the model when you do want markdown formatting in the response, include the string `Formatting re-enabled` on the first line of your developer message."
> 
> — *OpenAI Reasoning Best Practices*[^2]

### Optimize Costs with Reasoning Persistence

For `o3` and `o4-mini`, reasoning items can be preserved between tool calls to reduce token usage:

```javascript
const response = await client.responses.create({
  model: "o4-mini",
  store: true,  // Enable reasoning persistence
  input: [...],
  previous_response_id: "resp_abc123"  // Include previous reasoning
});
```

> "With `o3` and `o4-mini`, some reasoning items adjacent to function calls are included in the model's context to help improve model performance while using the least amount of reasoning tokens."
> 
> — *OpenAI Reasoning Best Practices*[^2]

**Best Practice:** Use the Responses API with `store: true` and pass all reasoning items from previous requests to avoid restarting reasoning from scratch.

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

### Visual Reasoning

o1 is the only reasoning model with vision capabilities. It excels at understanding complex visuals that GPT-4o struggles with:

| Visual Type | o1 Advantage |
|-------------|--------------|
| Architectural drawings | Identifies fixtures, materials, reads legends across pages |
| Financial charts | Understands relationships between data points |
| Complex tables | Parses ambiguous structure |
| Poor quality images | Better OCR and interpretation |

> "GPT-4o reached 50% accuracy on our hardest image classification tasks. o1 achieved an impressive 88% accuracy without any modifications to our pipeline."
> 
> — *SafetyKit (risk & compliance platform), via OpenAI*[^2]

### More Customer Success Stories

| Company | Use Case | Result |
|---------|----------|--------|
| **Hebbia** | Complex legal document analysis | "o1 yielded stronger results on 52% of complex prompts" |
| **Endex** | M&A due diligence | Found critical $75M loan provision in footnotes |
| **BlueFlame AI** | Shareholder equity calculations | Solved complex anti-dilution loops flawlessly |
| **Lindy.AI** | Agentic workflows (email, calendar) | "Agents became basically flawless overnight" |
| **CodeRabbit** | AI code reviews | 3x increase in product conversion rates |
| **Windsurf** | Complex software design | "Consistently produces high-quality, conclusive code" |
| **Braintrust** | LLM-as-Judge evaluations | F1 score improved from 0.12 to 0.74 |

---

## Frontend Development Stack

For GPT-5 frontend projects, OpenAI recommends:

| Category | Recommended |
|----------|-------------|
| **Framework** | Next.js (TypeScript), React |
| **Styling** | Tailwind CSS, shadcn/ui, Radix Themes |
| **Icons** | Material Symbols, Heroicons, Lucide |
| **Animation** | Motion |
| **Fonts** | Sans Serif, Inter, Geist, Mona Sans, IBM Plex Sans, Manrope |

> — *OpenAI GPT-5 Prompting Guide*[^4]

### Frontend Code Editing Rules

For consistent, high-quality frontend code, use structured prompts like this:

```xml
<<code_editing_rules>>
<<guiding_principles>>
- Clarity and Reuse: Every component should be modular and reusable
- Consistency: Adhere to a unified design system
- Simplicity: Favor small, focused components
- Visual Quality: Follow spacing, padding, hover states best practices
<</guiding_principles>>

<<frontend_stack_defaults>>
- Framework: Next.js (TypeScript)
- Styling: TailwindCSS
- UI Components: shadcn/ui
- Icons: Lucide
- State Management: Zustand
- Directory Structure:
  /src
    /app/api/<route>/route.ts  # API endpoints
    /(pages)                   # Page routes
    /components/               # UI building blocks
    /hooks/                    # Reusable React hooks
    /lib/                      # Utilities
    /stores/                   # Zustand stores
    /types/                    # Shared TypeScript types
<</frontend_stack_defaults>>

<<ui_ux_best_practices>>
- Visual Hierarchy: Limit typography to 4-5 font sizes
- Color Usage: 1 neutral base + up to 2 accent colors
- Spacing: Always use multiples of 4 for padding/margins
- State Handling: Use skeleton placeholders for loading
- Accessibility: Use semantic HTML and ARIA roles
<</ui_ux_best_practices>>
<</code_editing_rules>>
```

> — *OpenAI GPT-5 Prompting Guide*[^4]

---

## Tooling: Prompt Optimizer & Evals

### Prompt Optimizer

OpenAI's dashboard tool for automatic prompt improvement:

**Preparation:**
1. Create a dataset with prompt + evaluation data
2. Create **at least 3 rows** with responses
3. Add annotations (Good/Bad) + **detailed, specific critiques**
4. Build **narrowly-defined graders** for each desired property

**Optimization:**
1. Click "Optimize" → new improved version
2. Test the new prompt
3. Repeat: generate → annotate → optimize

> "The prompt optimizer is a chat interface in the dashboard, where you enter a prompt, and we optimize it according to current best practices."
> 
> — *OpenAI Prompt Optimizer Guide*[^5]

> "The effectiveness of prompt optimization depends on the quality of your graders. We recommend building narrowly-defined graders for each of the desired output properties where you see your prompt failing."
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

#### Create an Eval via API

```python
from openai import OpenAI
client = OpenAI()

eval_obj = client.evals.create(
    name="IT Ticket Categorization",
    data_source_config={
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {
                "ticket_text": {"type": "string"},
                "correct_label": {"type": "string"},
            },
            "required": ["ticket_text", "correct_label"],
        },
        "include_sample_schema": True,
    },
    testing_criteria=[
        {
            "type": "string_check",
            "name": "Match output to human label",
            "input": "{{ sample.output_text }}",
            "operation": "eq",
            "reference": "{{ item.correct_label }}",
        }
    ],
)
```

#### Test Data Format (JSONL)

```jsonl
{"item": {"ticket_text": "My monitor won't turn on!", "correct_label": "Hardware"}}
{"item": {"ticket_text": "I'm in vim and I can't quit!", "correct_label": "Software"}}
{"item": {"ticket_text": "Best restaurants in Cleveland?", "correct_label": "Other"}}
```

#### Run an Eval

```python
run = client.evals.runs.create(
    "YOUR_EVAL_ID",
    name="Categorization test run",
    data_source={
        "type": "responses",
        "model": "gpt-4.1",
        "input_messages": {
            "type": "template",
            "template": [
                {"role": "developer", "content": "Categorize into Hardware, Software, or Other."},
                {"role": "user", "content": "{{ item.ticket_text }}"},
            ],
        },
        "source": {"type": "file_id", "id": "YOUR_FILE_ID"},
    },
)
```

#### Monitor with Webhooks

Subscribe to eval events for automated monitoring:

| Event | Trigger |
|-------|---------|
| `eval.run.succeeded` | Run completed successfully |
| `eval.run.failed` | Run encountered an error |
| `eval.run.canceled` | Run was canceled |

> "To receive updates when a run succeeds, fails, or is canceled, create a webhook endpoint and subscribe to the `eval.run.succeeded`, `eval.run.failed`, and `eval.run.canceled` events."
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
