# Set up Git on Mac

> Install Git using Xcode Command Line Tools

---

## Cursor Prompt

Copy and paste this prompt into Cursor:

```
Hey! I'm new to Cursor and need help setting up Git on my Mac. I'm not very comfortable with the terminal, so please explain everything in simple terms.

Please do the following:

1. First, check if Git is already installed by running `git --version`

2. If Git is NOT installed, run `xcode-select --install` to start the installation. Then explain to me:
   - A popup window will appear asking me to install "Command Line Developer Tools"
   - I should click "Install" and wait (it takes 5-10 minutes)
   - Tell me to let you know when the installation popup says it's done

3. After I confirm it's done, verify the installation by running `git --version` again

4. If everything worked, celebrate with me and tell me I'm all set!

If anything goes wrong or looks like an error, please explain what it means in plain English and help me fix it. Don't assume I know what any technical terms mean.
```

---

## What It Does

1. Checks if Git is already installed
2. If not, runs `xcode-select --install` to install Command Line Tools
3. Walks you through the popup dialog
4. Verifies the installation worked

---

## Who This Is For

New to coding or the terminal? This prompt explains everything in plain English.

---

## Source

Content adapted from [Agrim Singh](https://www.agrimsingh.com/resources/setup-git-mac).

---

[Back to Setup Guides](README.md) | [Back to main README](../README.md)
