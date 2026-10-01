# Cursor Harness

A harness here is a tool that drives several agents from Cursor: the Cursor agent orchestrates, other models do the work in their own CLIs, and the results come back to Cursor for triage and your decisions. Each tool is a single file you @-mention, plus the scripts it calls.

| Tool | What it does |
|------|--------------|
| [second-opinion](second-opinion/) | Opus plans and implements in the Claude Code CLI, Codex reviews every change read-only; also PR review and module sweep (Windows) |

---

[Back to Tools & Resources](../README.md) | [Back to main README](../../README.md)
