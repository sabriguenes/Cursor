# C++ Cursor Rules

> **Production-ready rules for modern C++ development.**

By [Vinnie Falco](https://github.com/vinniefalco) • Source: [cppalliance/coro-io-context](https://github.com/cppalliance/coro-io-context)

---

## Rules

| File | Description |
|------|-------------|
| [cpp.mdc](cpp.mdc) | Class layout, coding conventions, error handling |
| [cpp-comments.mdc](cpp-comments.mdc) | Comment philosophy: explain WHY, not how |
| [cpp-javadoc.mdc](cpp-javadoc.mdc) | Javadoc/Doxygen documentation standards |
| [cmake.mdc](cmake.mdc) | CMake best practices, presets, no in-source builds |

## Commands

| File | Description |
|------|-------------|
| [build.md](build.md) | Build C++ projects with CMake |
| [commit.md](commit.md) | AI-generated conventional commit messages |
| [fix.md](fix.md) | Fix compile errors, then fix failing tests |

---

## Quick Start

```bash
# Copy all C++ rules to your project
mkdir -p .cursor/rules
cp *.mdc .cursor/rules/
```

---

## What's Included

### Coding Conventions
- Private data members first, public interface last
- `struct` if all public, otherwise `class`
- Protect `min`/`max` with parentheses: `(std::min)(a, b)`
- Idiomatic error checks: `ec.failed()` not `!!ec`

### Comment Style
- **Explain WHY, not how or what**
- Code should be self-documenting
- No ASCII-art dividers

### Documentation (Javadoc)
- Brief starts with action verb based on function type
- Section order: Brief → Description → @par → @throws → @param → @return
- Exception safety guarantees documented

### CMake
- Always use `cmake --preset`
- Never in-source builds
- Forbidden: `cmake .`, `cmake -B .`

---

## Attribution

These rules are by **[Vinnie Falco](https://github.com/vinniefalco)**, author of:
- [Boost.Beast](https://github.com/boostorg/beast) - HTTP/WebSocket
- [Boost.URL](https://github.com/boostorg/url) - URL parsing
- [Boost.JSON](https://github.com/boostorg/json) - JSON library

Licensed under MIT. Used with permission.
