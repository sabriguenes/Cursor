# Cursor IDE Cheatsheet

> Everything you need to know on one page. Print it, bookmark it, share it.

---

## Keyboard Shortcuts

### Essential Commands

| Action | Windows/Linux | macOS |
|--------|---------------|-------|
| **Open Command Palette** | `Ctrl+Shift+P` | `Cmd+Shift+P` |
| **Open AI Chat** | `Ctrl+L` | `Cmd+L` |
| **Inline Edit (Cmd+K)** | `Ctrl+K` | `Cmd+K` |
| **Accept Suggestion** | `Tab` | `Tab` |
| **Reject Suggestion** | `Esc` | `Esc` |
| **Toggle Sidebar** | `Ctrl+B` | `Cmd+B` |
| **Quick Open File** | `Ctrl+P` | `Cmd+P` |
| **Go to Definition** | `F12` | `F12` |
| **Find References** | `Shift+F12` | `Shift+F12` |

### AI-Specific

| Action | Windows/Linux | macOS |
|--------|---------------|-------|
| **Generate Code** | `Ctrl+K` | `Cmd+K` |
| **Edit Selection** | Select + `Ctrl+K` | Select + `Cmd+K` |
| **Explain Code** | Select + `Ctrl+L` | Select + `Cmd+L` |
| **Fix Error** | Click error + `Ctrl+K` | Click error + `Cmd+K` |
| **New Chat** | `Ctrl+Shift+L` | `Cmd+Shift+L` |

---

## @ Commands Reference

Use `@` in chat to add context:

| Command | What it does |
|---------|--------------|
| `@file` | Reference a specific file |
| `@folder` | Reference entire folder |
| `@codebase` | Search entire codebase |
| `@web` | Search the web for current info |
| `@docs` | Reference documentation |
| `@git` | Git history and changes |
| `@definitions` | Symbol definitions |
| `@problems` | Current errors/warnings |
| `@terminal` | Terminal output |
| `@clipboard` | Clipboard content |

### Pro Tips

```
@file:src/utils/auth.ts      # Specific file
@folder:src/components       # Entire folder
@codebase:"login flow"       # Semantic search
@web:latest React 19 features
```

---

## Model Selection Guide

### Quick Reference

| Model | Best For | Speed | Cost |
|-------|----------|-------|------|
| **Claude 3.5 Sonnet** | Complex reasoning, long code | Medium | $$ |
| **GPT-4o** | General coding, fast iteration | Fast | $$ |
| **GPT-5** | Agentic tasks, instruction following | Medium | $$$ |
| **Claude 3 Opus** | Difficult problems, nuanced tasks | Slow | $$$ |
| **o1/o3** | Complex planning, multi-step logic | Slow | $$$$ |
| **GPT-4o-mini** | Simple tasks, high volume | Very Fast | $ |

### When to Use What

```
Simple refactoring     → GPT-4o-mini
Bug fixing            → GPT-4o or Claude Sonnet
New feature           → Claude Sonnet or GPT-5
Architecture planning → o1/o3
Code review           → Claude Sonnet
```

---

## Chat Modes

### Agent Mode (Default)
- Full access to tools
- Can edit files, run commands
- Best for implementation tasks

### Ask Mode
- Read-only, no edits
- Great for questions and exploration
- Use: "Explain how this works"

### Plan Mode
- Creates step-by-step plans
- Good for complex tasks
- Review before execution

---

## Inline Edit (Cmd+K) Patterns

### Generate New Code
```
// Cmd+K: "Create a function that validates email addresses"
```

### Edit Selection
```
// Select code, then Cmd+K: "Add error handling"
// Select code, then Cmd+K: "Convert to async/await"
// Select code, then Cmd+K: "Add TypeScript types"
```

### Quick Fixes
```
// On error line, Cmd+K: "Fix this error"
// On slow code, Cmd+K: "Optimize for performance"
```

---

## Rules & Configuration

### Project Rules Location
```
your-project/
└── .cursor/
    └── rules/
        ├── general.mdc      # Always applied
        └── python.mdc       # Python files only
```

### Rule Template
```yaml
---
description: What this rule does
globs: ["**/*.py"]        # Optional: file patterns
alwaysApply: true         # true = always, false = contextual
---

Your instructions here...
```

### Global Settings
- `Ctrl+,` → Search "Cursor"
- Privacy Mode: Settings → Privacy → Enable
- Model selection: Bottom-left dropdown

---

## Common Prompting Patterns

### Be Specific
```
❌ "Make this better"
✅ "Refactor this function to use early returns and add error handling for null inputs"
```

### Provide Context
```
❌ "Fix the bug"
✅ "The login function returns undefined when the API returns 401. Handle this case by redirecting to /login"
```

### Step by Step for Complex Tasks
```
"Let's implement user authentication:
1. First, create the login endpoint
2. Then, add session management
3. Finally, protect the dashboard routes"
```

---

## Hidden Features

### Multi-File Editing
- Reference multiple files: `@file:a.ts @file:b.ts "update both to use new API"`

### Codebase Questions
- `@codebase "How does authentication work here?"`
- `@codebase "Where is the database connection configured?"`

### Image Input
- Paste screenshots of designs
- Paste error screenshots
- Paste diagrams

### Terminal Integration
- `@terminal` to reference output
- "Run npm test and fix any failures"

### Git Integration
- "What changed in the last 3 commits?"
- `@git "Explain recent changes to auth module"`

---

## Troubleshooting

### Cursor is Slow
1. Reduce open files
2. Close unused terminals
3. Disable unused extensions
4. Increase memory in settings

### Model Not Responding
1. Check internet connection
2. Verify API key (if using own key)
3. Try different model
4. Restart Cursor

### Privacy Concerns
1. Enable Privacy Mode
2. Use `.cursorignore` for sensitive files
3. See our [Enterprise Privacy Guide](../enterprise/)

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│  CURSOR QUICK REFERENCE                         │
├─────────────────────────────────────────────────┤
│  Ctrl+L     Chat with AI                        │
│  Ctrl+K     Inline edit                         │
│  Tab        Accept suggestion                   │
│  Esc        Reject suggestion                   │
│  @file      Add file context                    │
│  @codebase  Search project                      │
│  @web       Search internet                     │
├─────────────────────────────────────────────────┤
│  Simple task?     → GPT-4o-mini                 │
│  Normal coding?   → Claude Sonnet / GPT-4o      │
│  Complex logic?   → o1/o3                       │
└─────────────────────────────────────────────────┘
```

---

## More Resources

- [Cursor Rules Collection](../rules/) - Ready-to-use rules
- [Prompt Engineering Guide](../prompting/) - Master prompting
- [Enterprise Privacy Guide](../enterprise/) - Security best practices
- [Official Cursor Docs](https://docs.cursor.com)

---

*Part of the [Cursor Resources](https://github.com/sabriguenes/Cursor) collection*  
*Last updated: January 2026*
