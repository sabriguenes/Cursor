---
description: Fix compile errors then run and fix tests
---

# Fix Command

Build, fix compile errors, then run and fix tests until everything passes.

## Instructions

1. **Build the project:**

```bash
cmake --build build
```

2. **If compile errors occur:**
   - Read the error message carefully
   - Fix the issue in the source code
   - Rebuild and repeat until clean

3. **Run tests:**

```bash
ctest --test-dir build --output-on-failure
```

4. **If tests fail:**
   - Analyze the failure output
   - Fix the failing test or the code being tested
   - Re-run tests and repeat until all pass

## Loop Structure

```
┌─────────────────────────────────────┐
│           Build Project             │
└──────────────┬──────────────────────┘
               │
               ▼
        ┌──────────────┐
        │ Compile OK?  │──No──▶ Fix Error ──┐
        └──────┬───────┘                    │
               │ Yes                        │
               ▼                            │
        ┌──────────────┐                    │
        │  Run Tests   │◀───────────────────┘
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
        │ Tests Pass?  │──No──▶ Fix Test ───┐
        └──────┬───────┘                    │
               │ Yes                        │
               ▼                            │
           ✓ Done ◀─────────────────────────┘
```

---

*Based on [Vinnie Falco's](https://github.com/vinniefalco) fix command from [cppalliance/coro-io-context](https://github.com/cppalliance/coro-io-context)*
