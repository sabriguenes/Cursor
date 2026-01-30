# Cursor Rules Collection

> **Production-ready `.mdc` rules for Cursor IDE. Copy, paste, customize.**

![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## What are Cursor Rules?

Cursor Rules (`.mdc` files) guide the AI assistant's behavior in your project. They live in `.cursor/rules/` and are automatically applied.

---

## Available Rules

| Language | Folder | Source |
|----------|--------|--------|
| **C++** | [cpp/](cpp/) | [Vinnie Falco](https://github.com/vinniefalco) ([cppalliance](https://github.com/cppalliance/coro-io-context)) |

*More languages coming soon: Python, Rust, Go, TypeScript*

---

## Quick Start

```bash
# 1. Create rules directory
mkdir -p .cursor/rules

# 2. Copy the rules you need
cp cpp/*.mdc .cursor/rules/

# 3. Done! Cursor applies them automatically
```

---

## Contributing

Have rules for other languages? Add them!

1. Create a folder: `rules/<language>/`
2. Add your `.mdc` rules and a `README.md`
3. Submit a PR

---

## Attribution

C++ rules by **[Vinnie Falco](https://github.com/vinniefalco)** (Boost.Beast, Boost.URL, Boost.JSON author).

Source: [cppalliance/coro-io-context](https://github.com/cppalliance/coro-io-context)
