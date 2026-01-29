# Anthropic Claude Prompt Engineering Guide

> The Complete 2026 Guide to Claude Opus 4.5, Sonnet 4.5, and Agentic Workflows

*By Sabo Guenes | January 2026*

Claude 4.5 models represent a significant leap in AI capabilities. But with great power comes the need for precise prompting. After analyzing Anthropic's official documentation and engineering blog posts, I've compiled everything you need to know about prompting Claude effectively.

---

## The Fundamentals

### What Makes Claude 4.5 Different?

Claude 4.5 models have been trained for **more precise instruction following** than previous generations. This is both a strength and something to be aware of.

> "These models have been trained for more precise instruction following than previous generations of Claude models."
> 
> — *Anthropic Claude 4 Best Practices*[^1]

### Model Selection

| Model | Best For | Characteristics |
|-------|----------|-----------------|
| **Opus 4.5** | Complex coding, agents, long-horizon tasks | Most capable, effort parameter available |
| **Sonnet 4.5** | Balanced performance, daily tasks | Fast, cost-effective |
| **Haiku 4.5** | Quick responses, high volume | Fastest, lowest cost |

> "It's intelligent, efficient, and the best model in the world for coding, agents, and computer use."
> 
> — *Anthropic Claude Opus 4.5 Announcement*[^2]

---

## General Principles

### Be Explicit with Instructions

Claude 4.5 models respond well to clear, explicit instructions. Being specific about your desired output enhances results.

> "Claude 4.x models respond well to clear, explicit instructions. Being specific about your desired output can help enhance results."
> 
> — *Anthropic Claude 4 Best Practices*[^1]

**Instead of:**
```
Create an analytics dashboard
```

**Try:**
```
Create an analytics dashboard. Include as many relevant features and interactions as possible. Go beyond the basics to create a fully-featured implementation.
```

### Add Context for Better Performance

Providing context or motivation behind your instructions helps Claude understand your goals.

```
Format your response as bullet points because:
1. This will be used in a presentation
2. Executives need to scan quickly
3. Each point should be actionable
```

> "Providing context or motivation behind your instructions, such as explaining to Claude why such behavior is important, can help Claude 4.x models better understand your goals."
> 
> — *Anthropic Claude 4 Best Practices*[^1]

---

## XML Tags: Claude's Native Language

Claude was trained with XML-heavy data. Using XML tags dramatically improves prompt structure and output quality.

> "Use tags like `<instructions>`, `<example>`, and `<formatting>` to clearly separate different parts of your prompt. This prevents Claude from mixing up instructions with examples or context."
> 
> — *Anthropic XML Tags Guide*[^3]

### Why Use XML Tags?

| Benefit | Description |
|---------|-------------|
| **Clarity** | Clearly separate different parts of your prompt |
| **Accuracy** | Reduce errors from misinterpretation |
| **Flexibility** | Easy to modify sections without rewriting |
| **Parseability** | Extract specific parts from responses |

### Practical Example

```xml
<instructions>
Analyze the following contract for potential risks.
Focus on liability clauses and termination conditions.
</instructions>

<contract>
{{CONTRACT_TEXT}}
</contract>

<output_format>
Return your analysis in JSON with keys: risks, severity, recommendations
</output_format>
```

### Tagging Best Practices

1. **Be consistent**: Use the same tag names throughout
2. **Nest tags**: Use hierarchy for complex content: `<outer><inner></inner></outer>`
3. **Reference tags**: "Using the contract in `<contract>` tags..."

> "Combine XML tags with other techniques like multishot prompting (`<examples>`) or chain of thought (`<thinking>`, `<answer>`). This creates super-structured, high-performance prompts."
> 
> — *Anthropic XML Tags Guide*[^3]

---

## System Prompts: The Most Powerful Technique

Role prompting via system prompts is the most powerful way to shape Claude's behavior.

> "Role prompting is the most powerful way to use system prompts with Claude. The right role can turn Claude from a general assistant into your virtual domain expert!"
> 
> — *Anthropic System Prompts Guide*[^4]

### Why Use Role Prompting?

- **Enhanced accuracy** in complex scenarios (legal, financial analysis)
- **Tailored tone** (CFO's brevity vs. copywriter's flair)
- **Improved focus** on task-specific requirements

### Implementation

```python
import anthropic
client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-5-20251101",
    max_tokens=2048,
    system="You are a seasoned data scientist at a Fortune 500 company.",
    messages=[
        {"role": "user", "content": "Analyze this dataset for anomalies..."}
    ]
)
```

### Role Prompting Tips

- Put role definition in `system` parameter
- Put task-specific instructions in `user` turn
- Experiment with specificity: "data scientist" vs. "data scientist specializing in customer insight analysis for Fortune 500 companies"

---

## Chain of Thought (CoT) Prompting

Giving Claude space to think dramatically improves performance on complex tasks.

> "Stepping through problems reduces errors, especially in math, logic, analysis, or generally complex tasks."
> 
> — *Anthropic Chain of Thought Guide*[^5]

### Three CoT Methods

| Method | Complexity | Use Case |
|--------|------------|----------|
| **Basic** | Low | Simple reasoning tasks |
| **Guided** | Medium | Specific thinking steps needed |
| **Structured** | High | Need to separate thinking from answer |

### Basic CoT

```
Think step-by-step about this problem.
```

### Guided CoT

```
Think through this problem by:
1. Identifying the key variables
2. Considering edge cases
3. Proposing a solution
4. Validating your solution
```

### Structured CoT (Recommended)

```xml
<instructions>
Analyze this financial data. Show your reasoning in <thinking> tags,
then provide your final answer in <answer> tags.
</instructions>

<data>
{{FINANCIAL_DATA}}
</data>
```

**Output:**
```xml
<thinking>
First, I'll examine the revenue trends...
The Q3 dip correlates with...
This suggests...
</thinking>

<answer>
The company shows strong fundamentals with a temporary Q3 slowdown
due to seasonal factors. Recommendation: Hold with positive outlook.
</answer>
```

> "Always have Claude output its thinking. Without outputting its thought process, no thinking occurs!"
> 
> — *Anthropic Chain of Thought Guide*[^5]

---

## Extended Thinking for Complex Tasks

For the most challenging problems, Claude's extended thinking mode provides logarithmic accuracy improvements.

> "Claude often performs better with high level instructions to just think deeply about a task rather than step-by-step prescriptive guidance."
> 
> — *Anthropic Extended Thinking Tips*[^6]

### When to Use Extended Thinking

- Complex STEM problems
- Constraint optimization
- Multi-step analysis
- Code architecture decisions

### Key Insight: Less Prescription, More Freedom

**Instead of:**
```
Think through this math problem step by step:
1. First, identify the variables
2. Then, set up the equation
3. Next, solve for x
...
```

**Try:**
```
Please think about this math problem thoroughly and in great detail. 
Consider multiple approaches and show your complete reasoning.
Try different methods if your first approach doesn't work.
```

### Technical Considerations

- Minimum thinking budget: 1024 tokens
- Start small, increase as needed
- For >32K thinking tokens, use batch processing
- Extended thinking performs best in English

> "The model's creativity in approaching problems may exceed a human's ability to prescribe the optimal thinking process."
> 
> — *Anthropic Extended Thinking Tips*[^6]

---

## Opus 4.5 Specific Best Practices

### The Effort Parameter

Unique to Opus 4.5, the effort parameter lets you control token usage vs. thoroughness.

> "With our new effort parameter on the Claude API, you can decide to minimize time and spend or maximize capability."
> 
> — *Anthropic Claude Opus 4.5 Announcement*[^2]

| Effort Level | Use Case | Token Impact |
|--------------|----------|--------------|
| Low | Quick decisions | Fastest, cheapest |
| Medium | Balanced tasks | Matches Sonnet 4.5 quality |
| High | Complex analysis | Most thorough |

### Watch for Overengineering

Opus 4.5 tends to create extra files, add unnecessary abstractions, or build flexibility that wasn't requested.

```xml
<<avoid_overengineering>>
Avoid over-engineering. Only make changes that are directly requested or clearly necessary. Keep solutions simple and focused.

Don't add features, refactor code, or make "improvements" beyond what was asked. A bug fix doesn't need surrounding code cleaned up.

Don't create helpers, utilities, or abstractions for one-time operations.
<</avoid_overengineering>>
```

> "Claude Opus 4.5 has a tendency to overengineer by creating extra files, adding unnecessary abstractions, or building in flexibility that wasn't requested."
> 
> — *Anthropic Claude 4 Best Practices*[^1]

### System Prompt Sensitivity

Opus 4.5 is more responsive to system prompts than previous models. If your prompts were designed to reduce undertriggering, you may now see overtriggering.

**Instead of:**
```
CRITICAL: You MUST use this tool when...
```

**Try:**
```
Use this tool when...
```

> "If your prompts were designed to reduce undertriggering on tools or skills, Claude Opus 4.5 may now overtrigger. The fix is to dial back any aggressive language."
> 
> — *Anthropic Claude 4 Best Practices*[^1]

### Thinking Sensitivity

When extended thinking is disabled, Opus 4.5 is sensitive to the word "think."

**Replace:**
- "think" → "consider", "evaluate", "analyze"
- "think about" → "reflect on", "examine"

---

## Building Effective Agents

### Workflows vs. Agents

Anthropic distinguishes between two types of agentic systems:

| Type | Description | Use When |
|------|-------------|----------|
| **Workflows** | LLMs orchestrated through predefined code paths | Predictable, well-defined tasks |
| **Agents** | LLMs dynamically direct their own processes | Flexibility needed, open-ended problems |

> "Workflows are systems where LLMs and tools are orchestrated through predefined code paths. Agents are systems where LLMs dynamically direct their own processes and tool usage."
> 
> — *Anthropic Building Effective Agents*[^7]

### Common Workflow Patterns

#### 1. Prompt Chaining

Break tasks into sequential steps:

```
Input → LLM Call 1 → Gate Check → LLM Call 2 → Output
```

**Use for:** Marketing copy generation → Translation

#### 2. Routing

Classify input and direct to specialized handlers:

```
Input → Classifier → [Handler A | Handler B | Handler C] → Output
```

**Use for:** Customer service (general questions vs. refunds vs. technical support)

#### 3. Parallelization

Run multiple LLM calls simultaneously:

- **Sectioning**: Break task into independent subtasks
- **Voting**: Run same task multiple times for confidence

**Use for:** Code review (multiple vulnerability checks), content moderation

#### 4. Orchestrator-Workers

Central LLM dynamically breaks down tasks and delegates:

```
Input → Orchestrator → [Worker 1, Worker 2, ...] → Synthesize → Output
```

**Use for:** Complex coding tasks, multi-source research

### Agent Design Principles

1. **Maintain simplicity** in your agent's design
2. **Prioritize transparency** by showing planning steps
3. **Craft your ACI** (Agent-Computer Interface) through thorough tool documentation

> "Success in the LLM space isn't about building the most sophisticated system. It's about building the right system for your needs."
> 
> — *Anthropic Building Effective Agents*[^7]

---

## Long-Horizon Reasoning

Claude 4.5 models excel at tasks spanning extended sessions and multiple context windows.

### State Tracking Best Practices

| Method | Use For |
|--------|---------|
| **JSON files** | Structured data (test results, task status) |
| **Text files** | Progress notes, general context |
| **Git** | Change tracking, checkpoints |

### Multi-Context Window Workflows

1. **First window**: Set up framework (tests, setup scripts)
2. **Subsequent windows**: Iterate on todo-list
3. **Use memory tools**: Save state before context refresh

```xml
<<context_management>>
Your context window will be automatically compacted as it approaches its limit.
Do not stop tasks early due to token budget concerns. 
Save your current progress and state to memory before the context window refreshes.
Be as persistent and autonomous as possible.
<</context_management>>
```

> "Claude 4.5 models excel at long-horizon reasoning tasks with exceptional state tracking capabilities."
> 
> — *Anthropic Claude 4 Best Practices*[^1]

---

## Parallel Tool Calling

Claude 4.5 models aggressively execute tools in parallel. This is controllable:

### Maximize Parallel Execution

```xml
<<use_parallel_tool_calls>>
If you intend to call multiple tools and there are no dependencies between 
the tool calls, make all of the independent tool calls in parallel.

Maximize use of parallel tool calls where possible to increase speed and efficiency.

However, if some tool calls depend on previous calls, do NOT call these 
tools in parallel and instead call them sequentially.
<</use_parallel_tool_calls>>
```

### Reduce Parallel Execution

```
Execute operations sequentially with brief pauses between each step to ensure stability.
```

> "Sonnet 4.5 being particularly aggressive in firing off multiple operations simultaneously."
> 
> — *Anthropic Claude 4 Best Practices*[^1]

---

## Output Formatting Control

### Reduce Markdown and Bullet Points

```xml
<<avoid_excessive_markdown_and_bullet_points>>
When writing reports, documents, technical explanations, analyses, or any 
long-form content, write in clear, flowing prose using complete paragraphs.

Use standard paragraph breaks for organization and reserve markdown 
primarily for `inline code`, code blocks, and simple headings.

DO NOT use ordered lists or unordered lists unless:
a) presenting truly discrete items where a list format is best
b) the user explicitly requests a list

Instead of listing items with bullets or numbers, incorporate them 
naturally into sentences.
<</avoid_excessive_markdown_and_bullet_points>>
```

### Key Principles

1. **Tell Claude what to do** instead of what not to do
2. **Use XML format indicators**: "Write in `<<prose_paragraphs>>` tags"
3. **Match prompt style to desired output**

---

## Multishot Prompting (Examples)

Few-shot examples dramatically improve output quality.

> "When you provide Claude examples of how to think through problems, it will follow similar reasoning patterns."
> 
> — *Anthropic Extended Thinking Tips*[^6]

### Example: Classification Task

```xml
<instructions>
Classify customer feedback as Positive, Negative, or Neutral.
</instructions>

<examples>
<example>
<input>The product arrived quickly and works great!</input>
<output>Positive</output>
</example>

<example>
<input>It's okay, nothing special.</input>
<output>Neutral</output>
</example>

<example>
<input>Broke after two days. Waste of money.</input>
<output>Negative</output>
</example>
</examples>

<task>
Classify: "Decent quality but shipping took forever."
</task>
```

### Best Practices

- Include 3-5 diverse examples
- Cover edge cases
- Match the complexity of your actual task

---

## Code Exploration and Hallucination Prevention

### Encourage Code Exploration

Opus 4.5 can be conservative when exploring code. Add explicit instructions:

```xml
<<investigate_before_answering>>
ALWAYS read and understand relevant files before proposing code edits.
Do not speculate about code you have not inspected.

If the user references a specific file/path, you MUST open and inspect it 
before explaining or proposing fixes.

Be rigorous and persistent in searching code for key facts.
<</investigate_before_answering>>
```

### Minimize Hallucinations

```xml
<<grounded_answers>>
Never speculate about code you have not opened.
If the user references a specific file, you MUST read the file before answering.

Make sure to investigate and read relevant files BEFORE answering questions.
Give grounded and hallucination-free answers.
<</grounded_answers>>
```

> "Claude 4.x models are less prone to hallucinations and give more accurate, grounded, intelligent answers based on the code."
> 
> — *Anthropic Claude 4 Best Practices*[^1]

---

## Practical Recommendations

### 1. Start Simple

> "We recommend finding the simplest solution possible, and only increasing complexity when needed."
> 
> — *Anthropic Building Effective Agents*[^7]

### 2. Use the Right Model

- **Opus 4.5**: Complex, multi-step tasks
- **Sonnet 4.5**: Daily work, balanced performance
- **Haiku 4.5**: High volume, quick responses

### 3. Pin Model Versions

```python
model="claude-opus-4-5-20251101"  # Specific snapshot
model="claude-opus-4-5"          # May change over time
```

### 4. Test with Real Data

Build evaluations early. Don't wait until production.

### 5. Iterate on Prompts

Read Claude's output, identify issues, refine prompts. This is an iterative process.

---

## References

[^1]: Anthropic. "Prompting Best Practices." *Anthropic Documentation*, January 2026. https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices

[^2]: Anthropic. "Introducing Claude Opus 4.5." *Anthropic News*, November 2025. https://www.anthropic.com/news/claude-opus-4-5

[^3]: Anthropic. "Use XML Tags to Structure Your Prompts." *Anthropic Documentation*, January 2026. https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags

[^4]: Anthropic. "Giving Claude a Role with a System Prompt." *Anthropic Documentation*, January 2026. https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/system-prompts

[^5]: Anthropic. "Let Claude Think (Chain of Thought Prompting)." *Anthropic Documentation*, January 2026. https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/chain-of-thought

[^6]: Anthropic. "Extended Thinking Tips." *Anthropic Documentation*, January 2026. https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/extended-thinking-tips

[^7]: Anthropic. "Building Effective Agents." *Anthropic Engineering Blog*, December 2024. https://www.anthropic.com/engineering/building-effective-agents

---

*Have questions? Contact me at [cursorconsulting.org](https://cursorconsulting.org)*
