# Set up Git on Windows

> Install Git using winget or the official installer

---

## Cursor Prompt

Copy and paste this prompt into Cursor:

```
Hey! I'm new to Cursor and need help setting up Git on my Windows computer. I'm not very comfortable with the terminal, so please explain everything in simple terms.

Please do the following:

1. First, check if Git is already installed by running `git --version`

2. If Git is NOT installed, try installing it with `winget install Git.Git`
   - If winget works, wait for it to complete and tell me what's happening
   - If winget doesn't work or isn't available, tell me to download Git from https://git-scm.com/download/win and run the installer with all default options, then come back and let you know when it's done

3. After installation, I may need to restart Cursor for it to find Git. Tell me if I need to do this.

4. Verify the installation by running `git --version`

5. If everything worked, celebrate with me and tell me I'm all set!

If anything goes wrong or looks like an error, please explain what it means in plain English and help me fix it. Don't assume I know what any technical terms mean.
```

---

## What It Does

1. Checks if Git is already installed
2. Tries `winget install Git.Git` first (fastest method)
3. Falls back to manual download if winget isn't available
4. Tells you if you need to restart Cursor
5. Verifies the installation worked

---

## Who This Is For

New to coding or the terminal? This prompt explains everything in plain English.

---

## Source

Content adapted from [Agrim Singh](https://www.agrimsingh.com/resources/setup-git-windows).

---

[Back to Setup Guides](README.md) | [Back to main README](../README.md)
