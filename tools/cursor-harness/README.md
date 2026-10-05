# Cursor Harness

A harness here is a tool that drives several agents from Cursor: the Cursor agent orchestrates, other models do the work in their own CLIs, and the results come back to Cursor for triage and your decisions. Each tool is a single file you @-mention; everything it runs is inside that file.

**The Foreman**\
_[foreman/foreman.md](foreman/foreman.md)_\
"When they disagree I do not take sides. I put a level on the wall." The model you pick in Cursor's agent chat becomes the Foreman and writes no code itself: it hands your plan to Opus, which builds it step by step in the Claude Code CLI, while Codex checks every change read-only in the Codex CLI and a test settles every dispute between them. Everything that is hard to undo comes to you, one question at a time. It works in three modes, develop, review and sweep, plus a one-time setup. Run it and you bring the drawings, and the walls come back inspected, with the keys still in your hand.

---

[Back to Tools & Resources](../README.md) | [Back to main README](../../README.md)
