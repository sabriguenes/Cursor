---
description: Stage all changes and commit with AI-generated message
---

# Git Commit with Generated Message

Stage all changes and commit with a detailed, conventional commit message.

## Instructions

1. **Stage all changes:**

```bash
git add -A
```

2. **Show what will be committed:**

```bash
git diff --cached --stat
```

3. **Get the detailed diff for analysis:**

```bash
git diff --cached
```

4. **Generate a commit message** following this format:

- **Subject line**: Use conventional commits style with a concise summary under 72 characters
- **Body**: Add a blank line, then bullet points describing the specific changes

### Conventional Commit Types

| Type | Description |
|------|-------------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation only |
| `refactor:` | Code change that neither fixes a bug nor adds a feature |
| `test:` | Adding or updating tests |
| `chore:` | Maintenance tasks |
| `perf:` | Performance improvement |
| `style:` | Formatting, missing semicolons, etc. |

### Example Format

```
feat: add compression support and improve error handling

- Add Brotli encode/decode functions in src/compress.cpp
- Fix null pointer check in path normalization
- Remove deprecated legacy API functions
- Update unit tests for new compression interface
```

5. **Commit with the generated message:**

```bash
git commit -m "<type>: <subject>

<body>"
```

6. **Show the result:**

```bash
git log -1 --oneline
```

---

*Based on [Vinnie Falco's](https://github.com/vinniefalco) commit command from [cppalliance/coro-io-context](https://github.com/cppalliance/coro-io-context)*
