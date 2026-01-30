# Connect to GitHub

> Authenticate with GitHub CLI so you can push and pull

---

## Cursor Prompt

Copy and paste this prompt into Cursor:

```
Hey! I need help connecting Cursor to my GitHub account so I can push and pull code. I'm not very comfortable with the terminal, so please explain everything in simple terms.

Please do the following:

1. First, check if the GitHub CLI is installed by running `gh --version`

2. If it's NOT installed:
   - On Mac: First check if Homebrew is installed with `brew --version`. If Homebrew is NOT installed, run `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` and explain to me: the terminal will ask me to press ENTER to continue, then ask for my Mac password (the screen will stay blank as I type it - that's normal). Wait for me to confirm Homebrew finished installing. Then run `brew install gh`
   - On Windows: Run `winget install GitHub.cli`

3. Once GitHub CLI is installed, run `gh auth login` and walk me through what happens:
   - Tell me to select "GitHub.com" when asked
   - Tell me to select "HTTPS" for the protocol
   - Tell me to select "Login with a web browser"
   - A code will appear in the terminal - tell me to copy it
   - My browser will open to GitHub - tell me to paste the code there and authorize
   - Wait for me to confirm I've done this

4. Verify it worked by running `gh auth status`

5. If everything worked, celebrate with me and explain that I can now push and pull from GitHub!

If anything goes wrong or looks like an error, please explain what it means in plain English and help me fix it. Don't assume I know what any technical terms mean.
```

---

## What It Does

1. Checks if GitHub CLI (`gh`) is installed
2. Installs it via Homebrew (Mac) or winget (Windows) if needed
3. Walks you through `gh auth login` step by step
4. Opens your browser to authorize the connection
5. Verifies everything worked

---

## After This

You'll be able to push commits to GitHub and pull from your repos directly in Cursor.

---

## Who This Is For

Have Git installed but need to connect to GitHub? This guide walks you through authentication.

---

## Source

Content adapted from [Agrim Singh](https://www.agrimsingh.com/resources/connect-github).

---

[Back to Setup Guides](README.md) | [Back to main README](../README.md)
