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

> *Master the art of prompting GPT-5, reasoning models, and beyond.*

A comprehensive guide based on OpenAI's 2026 documentation, including the Cursor team's real-world learnings from GPT-5 integration.

| Guide | Language |
|-------|----------|
| [OpenAI Prompt Engineering Guide](prompting/prompt-engineering-en.md) | English |
| [OpenAI Prompt Engineering Leitfaden](prompting/prompt-engineering-de.md) | Deutsch |

**What you'll learn:**
- GPT-5 vs Reasoning Models (o3, o4-mini) - when to use which
- Prompt Caching: Save up to 90% on costs
- Agentic workflow control and eagerness levels
- Real case study: Cursor's GPT-5 prompt tuning

---

## Repository Structure

```
Cursor/
├── enterprise/                    # Enterprise Privacy & Security
│   ├── README.md                  # Section overview
│   ├── privacy-guide-en.md        # English guide
│   └── privacy-guide-de.md        # German guide
│
├── prompting/                     # Prompt Engineering
│   ├── README.md                  # Section overview
│   ├── prompt-engineering-en.md   # English guide
│   └── prompt-engineering-de.md   # German guide
│
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

## Acknowledgments

Special thanks to:

- The **Cursor team** (Nathan, Nick, Anais) for building an amazing product and being transparent about security
- **Nao** and the Cursor Ambassador community for the knowledge exchange
- Everyone at **Cafe Cursor Berlin** for the great discussions

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
