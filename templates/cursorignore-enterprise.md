# Enterprise .cursorignore Template

Copy this content to `.cursorignore` in your project root.

---

```gitignore
# ============================================
# ENTERPRISE .CURSORIGNORE TEMPLATE
# ============================================
# Prevents sensitive files from being indexed
# by Cursor AI's codebase indexing feature.
# ============================================

# ----------------------
# SECRETS & CREDENTIALS
# ----------------------
.env
.env.*
.env.local
.env.development
.env.production
.env.staging
*.env

# API Keys & Tokens
**/secrets/**
**/credentials/**
**/.secrets/**
**/api-keys/**

# Certificate files
*.pem
*.key
*.crt
*.cer
*.p12
*.pfx
*.jks

# SSH Keys
id_rsa
id_rsa.pub
id_ed25519
id_ed25519.pub
*.ppk

# ----------------------
# CONFIGURATION
# ----------------------
# Production configs (may contain secrets)
config/production.*
config/prod.*
**/config/secrets.*
**/config/credentials.*

# Terraform state (contains infrastructure secrets)
*.tfstate
*.tfstate.*
.terraform/

# Ansible vault files
**/vault.yml
**/vault.yaml
**/*vault*.yml

# ----------------------
# DATABASE
# ----------------------
# Database dumps (may contain PII)
*.sql
*.dump
*.sqlite
*.db

# Migration files with sensitive data
**/migrations/seed_production*

# ----------------------
# LOGS & AUDIT
# ----------------------
# Log files (may contain sensitive data)
*.log
**/logs/**
**/log/**

# Audit trails
**/audit/**
**/audit-logs/**

# ----------------------
# VENDOR & DEPENDENCIES
# ----------------------
# Large directories that don't need indexing
node_modules/
vendor/
.venv/
venv/
__pycache__/
.cache/
dist/
build/
.next/
.nuxt/

# Package lock files (large, not useful for AI)
package-lock.json
yarn.lock
pnpm-lock.yaml
composer.lock
Gemfile.lock
poetry.lock
Cargo.lock

# ----------------------
# GENERATED & BINARY
# ----------------------
# Binary files
*.exe
*.dll
*.so
*.dylib
*.bin

# Compiled files
*.class
*.pyc
*.pyo
*.o
*.a

# Archives
*.zip
*.tar
*.tar.gz
*.rar
*.7z

# Media (unless you need AI to understand them)
*.mp4
*.mov
*.avi
*.mp3
*.wav

# Large data files
*.csv
*.parquet
*.avro

# ----------------------
# IDE & TOOLS
# ----------------------
.idea/
.vscode/
*.swp
*.swo
*~

# ----------------------
# TESTING
# ----------------------
# Test fixtures with sensitive mock data
**/fixtures/production*
**/fixtures/sensitive*
**/__fixtures__/production*

# Coverage reports
coverage/
.coverage
*.lcov

# ----------------------
# DOCUMENTATION
# ----------------------
# Internal docs that shouldn't be indexed
**/internal-docs/**
**/confidential/**
**/restricted/**

# ----------------------
# CUSTOM PATTERNS
# ----------------------
# Add your organization-specific patterns below:

# Example: proprietary algorithms
# **/algorithms/proprietary/**

# Example: customer data
# **/customer-data/**

# Example: legal documents
# **/legal/**
```

---

## Usage

1. Copy the content above to `.cursorignore` in your project root
2. Customize the "CUSTOM PATTERNS" section for your organization
3. Test by checking Cursor's indexing status
4. Commit to version control

## Verification

After creating `.cursorignore`, verify it's working:

1. Open Cursor Settings (`Ctrl+Shift+J`)
2. Check "Codebase Indexing" status
3. Verify excluded files aren't being indexed

---

*Need help customizing? Contact [cursorconsulting.org](https://cursorconsulting.org)*
