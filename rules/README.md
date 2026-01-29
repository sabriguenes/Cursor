# Cursor Rules Collection

> Production-ready `.mdc` rules for Cursor IDE. Copy, paste, customize.

![Rules](https://img.shields.io/badge/Rules-5%20Starter-blue)
![Ready](https://img.shields.io/badge/Status-Copy%20Paste%20Ready-brightgreen)

---

## What are Cursor Rules?

Cursor Rules (`.mdc` files) are instructions that guide the AI assistant's behavior in your project. They live in `.cursor/rules/` and are automatically applied based on file patterns.

### Rule Structure

```yaml
---
description: Short description of what this rule does
globs: ["**/*.py"]  # Optional: only apply to matching files
alwaysApply: false  # true = always active, false = context-dependent
---

Your instructions here...
```

---

## Available Rules

### General Purpose

| Rule | Description | Use Case |
|------|-------------|----------|
| [clean-code.mdc](./clean-code.mdc) | Clean code principles | All projects |
| [documentation.mdc](./documentation.mdc) | Auto-documentation standards | API, libraries |
| [testing.mdc](./testing.mdc) | Test-first development | TDD workflows |

### Language-Specific

| Rule | Description | Use Case |
|------|-------------|----------|
| [python.mdc](./python.mdc) | Python best practices | Python projects |
| [typescript.mdc](./typescript.mdc) | TypeScript/React patterns | Frontend, Node.js |

---

## Installation

1. Create `.cursor/rules/` in your project root (if it doesn't exist)
2. Copy the desired `.mdc` file into that folder
3. Customize as needed
4. Cursor will automatically apply the rules

```bash
# Quick setup
mkdir -p .cursor/rules
cp clean-code.mdc .cursor/rules/
```

---

## Customization Tips

### Scope Rules by File Type

```yaml
---
globs: ["**/*.tsx", "**/*.jsx"]
---
# This rule only applies to React components
```

### Combine Multiple Rules

You can have multiple `.mdc` files - they stack. Use specific globs to avoid conflicts.

### Override for Specific Files

More specific glob patterns take precedence over general ones.

---

## Contributing

Have a useful rule? Submit a PR!

1. Follow the existing format
2. Include clear description
3. Test in a real project
4. Document the use case

---

## Related Resources

- [Cursor Rules Documentation](https://docs.cursor.com/context/rules)
- [Prompt Engineering Guide](../prompting/)
- [Enterprise Privacy Guide](../enterprise/)

---

*Part of the [Cursor Resources](https://github.com/sabriguenes/Cursor) collection*
