# Cursor Auto-Approved Mode Transitions

## Keywords
mode switching, agent mode, plan mode, auto-approve, mode transitions, cursor settings, agent settings, auto-run, timeout, approval, debug mode, ask mode

---

## The Problem

When the Cursor agent wants to switch modes (e.g., from Agent to Plan mode), it asks for your approval. This approval has a **timeout** - if you're not looking at Cursor when the popup appears, it will expire and the mode switch won't happen.

---

## The Solution: Auto-Approved Mode Transitions

You can configure Cursor to **automatically approve mode switches** without asking you.

### Location

```
Cursor Settings > Agent > Auto-run > Auto-Approved Mode Transitions
```

Or press `Ctrl + Shift + J` (Windows) / `Cmd + Shift + J` (Mac) to open Cursor Settings directly.

---

## Syntax

The syntax for auto-approved transitions is:

```
source_mode->target_mode
```

### Available Modes

| Mode | Description |
|------|-------------|
| `agent` | Default implementation mode with full tool access |
| `plan` | Read-only collaborative mode for designing approaches |
| `debug` | Systematic troubleshooting mode for bugs |
| `ask` | Read-only mode for exploring code and answering questions |

---

## All Possible Transitions

Copy and paste these into the setting to enable **all** automatic mode transitions:

```
agent->plan, agent->debug, agent->ask, plan->agent, plan->debug, plan->ask, debug->agent, debug->plan, debug->ask, ask->agent, ask->plan, ask->debug
```

### Alternative: One per line

```
agent->plan
agent->debug
agent->ask
plan->agent
plan->debug
plan->ask
debug->agent
debug->plan
debug->ask
ask->agent
ask->plan
ask->debug
```

---

## Common Configurations

### Trust All Mode Changes (Recommended for Power Users)

```
agent->plan, agent->debug, agent->ask, plan->agent, plan->debug, plan->ask, debug->agent, debug->plan, debug->ask, ask->agent, ask->plan, ask->debug
```

### Only Agent <-> Plan (Conservative)

```
agent->plan, plan->agent
```

### Agent to Everything (Agent can switch out, but needs approval to switch back)

```
agent->plan, agent->debug, agent->ask
```

---

## Quick Setup Guide

1. Open Cursor Settings (`Ctrl + Shift + J` / `Cmd + Shift + J`)
2. Navigate to **Agent** section
3. Find **Auto-run** subsection
4. Locate **Auto-Approved Mode Transitions**
5. Paste your desired transitions (comma-separated)
6. Settings save automatically

---

## Feature Request

As of January 2026, there's no "Enable All" button in the UI. Users have requested a quick-add button that would paste all transitions automatically. For now, copy the full list from above.

---

## Tips

- **Trust the agent**: If you find yourself always approving mode switches, just enable all transitions
- **Start conservative**: Begin with `agent->plan, plan->agent` and add more as needed
- **Debug mode**: Consider auto-approving `agent->debug` since debugging often needs quick mode switches
- **No undo needed**: These settings can be changed anytime without side effects

---

## Related Settings

| Setting | Location | Description |
|---------|----------|-------------|
| Auto-run Mode | Agent > Auto-run | Controls which tools run automatically |
| Yolo Mode | Agent > Auto-run | Runs all tools without approval |
| Safe Mode | Agent > Auto-run | Requires approval for all changes |

---

## Source

This information was shared by Colin Mueller in the Cursor community (January 2026).
