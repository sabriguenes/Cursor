<p align="center">
  <img src="https://cursor.com/brand/logo.svg" alt="Cursor Logo" width="80" height="80">
</p>

<h1 align="center">Cursor Resources</h1>

<p align="center">
  <strong>Open-source guides for AI-assisted development</strong><br>
  Enterprise privacy, prompt engineering, and best practices for Cursor IDE
</p>

<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://cursor.com"><img src="https://img.shields.io/badge/Cursor-AI%20Editor-blue" alt="Cursor"></a>
  <a href="https://cursorconsulting.org"><img src="https://img.shields.io/badge/Cursor-Ambassador-purple" alt="Ambassador"></a>
  <a href="https://github.com/sabriguenes/Cursor/stargazers"><img src="https://img.shields.io/github/stars/sabriguenes/Cursor?style=social" alt="GitHub Stars"></a>
</p>

<p align="center">
  <a href="#-vision">Vision</a> •
  <a href="#-guides">Guides</a> •
  <a href="#-repository-structure">Structure</a> •
  <a href="#-about-me">About Me</a> •
  <a href="#-contributing">Contributing</a>
</p>

---

## The Vision

AI-assisted development is transforming how we write software. But with great power comes great responsibility—and great confusion.

**This repository exists to bridge the gap** between cutting-edge AI capabilities and practical, real-world implementation:

- **For enterprises**: Understand the privacy implications before adopting AI tools
- **For developers**: Master prompt engineering to 10x your productivity
- **For teams**: Get actionable best practices, not marketing fluff
- **For everyone**: Discover the best AI-powered developer tools

Everything here is:
- **Open source** - Use it, share it, improve it
- **Well-researched** - Sourced from official documentation and real-world experience
- **Bilingual** - Available in English and German
- **Practical** - No theory without application

---

## Guides

### [Enterprise Privacy & Security](enterprise/)

> *"Will our proprietary code be safe?"*

The question every CTO asks before adopting AI coding assistants. This guide provides the answers.

| Guide | Language |
|-------|----------|
| [Enterprise Privacy Guide](enterprise/privacy-guide-en.md) | English |
| [Enterprise Datenschutz-Leitfaden](enterprise/privacy-guide-de.md) | Deutsch |

**What you'll learn:**
- How Cursor's Merkle tree indexing works
- Privacy Mode vs Share Data (and what's actually stored)
- Zero Data Retention agreements with OpenAI, Anthropic, etc.
- GDPR compliance and practical `.cursorignore` recommendations

---

### [Prompt Engineering](prompting/)

> *Master the art of prompting AI models — organized by provider.*

Comprehensive guides with citations to official documentation.

| Provider | Guides | Topics |
|----------|--------|--------|
| [**OpenAI**](prompting/openai/) | [EN](prompting/openai/prompt-engineering-en.md) / [DE](prompting/openai/prompt-engineering-de.md) | GPT-5, o3, o4-mini, Responses API |
| [**Anthropic**](prompting/anthropic/) | [EN](prompting/anthropic/prompt-engineering-en.md) / [DE](prompting/anthropic/prompt-engineering-de.md) | Opus 4.5, Sonnet 4.5, Agentic Workflows |

**What you'll learn:**
- GPT-5 vs Reasoning Models (o3, o4-mini) - when to use which
- Claude Opus 4.5: XML Tags, Extended Thinking, Effort Parameter
- Prompt Caching, Structured Outputs, Evals
- Building Effective Agents (Anthropic patterns)

*More providers coming soon (Gemini, etc.)*

---

### [Cursor Rules Collection](rules/)

> *Production-ready `.mdc` rules for Cursor IDE. Copy, paste, customize.*

Rules that guide Cursor's AI behavior for consistent, high-quality code.

| Language | Folder | Source |
|----------|--------|--------|
| **C++** | [rules/cpp/](rules/cpp/) | [Vinnie Falco](https://github.com/vinniefalco) |

**What you'll get:**
- C++ class layout and coding conventions
- Javadoc/Doxygen documentation standards
- CMake best practices (presets, no in-source builds)
- Comment philosophy: explain WHY, not how

*Based on rules from [cppalliance/coro-io-context](https://github.com/cppalliance/coro-io-context) with permission.*

---

### [Tools & Resources](tools/)

> *Curated guides to the best AI-powered developer tools.*

Opinionated, well-researched overviews of tools that are changing how developers work.

| Guide | Description |
|-------|-------------|
| [AI Code Search Tools](tools/ai-code-search-tools.md) | The definitive guide to AI-powered code search — Greptile, Bloop, Phind, Sourcegraph & more |

**What you'll learn:**
- Chat with your codebase: Greptile (cloud) vs Bloop (local/privacy-first)
- Search the web for code: Phind, AI GitHub Search
- Zero-install web tools: Grep.app, Repogrep, GitSeek, PublicWWW, SearchCode
- Enterprise solutions: Sourcegraph + Cody, GitHub Code Search
- Hidden gems: Cursor @Codebase, Sturdy CLI, Zilliz/SolidGPT

---

### [Setup Guides](resources/)

> *New to Cursor? Start here.*

Interactive prompts that walk you through setting up Git and GitHub.

| Guide | Description |
|-------|-------------|
| [Set up Git on Mac](resources/setup-git-mac.md) | Install Git using Xcode Command Line Tools |
| [Set up Git on Windows](resources/setup-git-windows.md) | Install Git using winget or the official installer |
| [Verify My Setup](resources/verify-setup.md) | Check if Git, Node.js, and Python are configured correctly |
| [Connect to GitHub](resources/connect-github.md) | Authenticate with GitHub CLI so you can push and pull |

**How to use:**
1. Copy the prompt from the guide you need
2. Paste it into Cursor's chat
3. Follow the AI's instructions step by step

*Content adapted from [Agrim Singh's Cursor Setup Resources](https://www.agrimsingh.com/resources/)*

---

## Repository Structure

```
Cursor/
├── enterprise/                    # Enterprise Privacy & Security
│   ├── README.md                  # Section overview
│   ├── privacy-guide-en.md        # English guide
│   └── privacy-guide-de.md        # German guide
│
├── prompting/                     # Prompt Engineering (by provider)
│   ├── README.md                  # Overview of all prompting guides
│   ├── openai/                    # OpenAI-specific guides
│   │   ├── README.md              # OpenAI guide overview & verification
│   │   ├── prompt-engineering-en.md   # English (with citations)
│   │   └── prompt-engineering-de.md   # German (with citations)
│   └── anthropic/                 # Anthropic Claude guides
│       ├── README.md              # Anthropic guide overview & verification
│       ├── prompt-engineering-en.md   # English (with citations)
│       └── prompt-engineering-de.md   # German (with citations)
│
├── rules/                         # Cursor Rules Collection (.mdc)
│   ├── README.md                  # Overview & quick start
│   └── cpp/                       # C++ rules (Vinnie Falco)
│       ├── README.md              # C++ overview
│       ├── cpp.mdc                # Coding conventions
│       ├── cpp-comments.mdc       # Comment philosophy
│       ├── cpp-javadoc.mdc        # Documentation standards
│       ├── cmake.mdc              # CMake best practices
│       ├── build.md               # Build command
│       ├── commit.md              # Commit command
│       └── fix.md                 # Fix command
│
├── resources/                     # Setup Guides (for beginners)
│   ├── README.md                  # Section overview
│   ├── setup-git-mac.md           # Git installation on Mac
│   ├── setup-git-windows.md       # Git installation on Windows
│   ├── verify-setup.md            # Verify dev environment
│   └── connect-github.md          # GitHub CLI authentication
│
├── tools/                         # Tools & Resources (curated guides)
│   ├── README.md                  # Section overview
│   └── ai-code-search-tools.md   # AI Code Search Tools guide
│
├── .github/                       # GitHub Templates
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
│
├── CONTRIBUTING.md                # Contribution guidelines
├── LICENSE                        # MIT License
└── README.md                      # You are here
```

More guides coming soon. Have a suggestion? [Open an issue](https://github.com/sabriguenes/Cursor/issues)!

---

## About Me

<img src="https://avatars.githubusercontent.com/sabriguenes" width="100" align="left" style="margin-right: 20px; border-radius: 50%;">

**Sabo Guenes**

Founder of [Xrock GmbH](https://xrock.io) and **Cursor Ambassador** based in Heidelberg, Germany.

After attending Cafe Cursor events across the US, Germany, and Europe, and consulting with enterprises on AI adoption, I've compiled these resources to help teams navigate the rapidly evolving landscape of AI-assisted development.

<br clear="left"/>

### Connect With Me

| Platform | Link |
|----------|------|
| **Website** | [cursorconsulting.org](https://cursorconsulting.org) |
| **LinkedIn** | [linkedin.com/in/sabriguenes](https://linkedin.com/in/sabriguenes) |
| **Company** | [xrock.io](https://xrock.io) |
| **Email** | [info@xrock.io](mailto:info@xrock.io) |

### Consulting Services

Need help implementing Cursor in your organization?

- Enterprise workshops & team onboarding
- Security best practices consulting
- Custom workflow optimization
- Bug investigation & fixes
- First-time setup assistance

**Let's talk:** [cursorconsulting.org](https://cursorconsulting.org)

---

## Contributing

This is an open-source project and contributions are welcome!

### How to Contribute

1. **Found an error?** Open an issue or submit a PR
2. **Have a suggestion?** Start a discussion
3. **Want to add content?** Fork, write, and submit a PR
4. **Translated content?** Additional languages welcome!

### Show Your Support

If you find these resources helpful:

- **Star this repo** - It helps others discover it
- **Share it** - With your team, on LinkedIn, wherever
- **Contribute** - Every improvement helps the community

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

You're free to use, modify, and distribute these resources. Attribution appreciated but not required.

---

<p align="center">
  <strong>If you find this helpful, please give it a star!</strong><br><br>
  <a href="https://github.com/sabriguenes/Cursor/stargazers">
    <img src="https://img.shields.io/github/stars/sabriguenes/Cursor?style=for-the-badge&logo=github" alt="Star on GitHub">
  </a>
</p>

<p align="center">
  Made with curiosity by <a href="https://cursorconsulting.org">Sabo Guenes</a>
</p>
