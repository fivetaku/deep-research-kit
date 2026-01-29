# Installation Guide

## Prerequisites

- Claude Code CLI installed and configured
- Python 3.8+ (for orchestrator script)
- Node.js 16+ (for npx installation)

---

## Installation Methods

### Method 1: npx (Recommended)

```bash
npx github:fivetaku/deep-research-kit
```

This automatically:
- Detects Claude Code or Codex CLI
- Copies skill files to `.claude/skills/` or `.codex/skills/`
- Creates `RESEARCH/` folder for outputs
- Copies query prompts to `prompts/`

**Options:**
```bash
# Specify target
npx github:fivetaku/deep-research-kit --target claude
npx github:fivetaku/deep-research-kit --target codex
npx github:fivetaku/deep-research-kit --target both

# Force overwrite existing
npx github:fivetaku/deep-research-kit --force
```

### Method 2: Manual Installation

```bash
# Clone the repository
git clone https://github.com/fivetaku/deep-research-kit.git
cd deep-research-kit

# Copy to your project (project-specific)
cp -r skills/deep-research YOUR_PROJECT/.claude/skills/

# Or copy to home directory (global)
mkdir -p ~/.claude/skills
cp -r skills/deep-research ~/.claude/skills/
```

### Method 3: Claude Code Plugin

```bash
# In Claude Code
/plugin marketplace add fivetaku/deep-research-kit
/plugin install deep-research@fivetaku-plugins
```

> Note: Plugin installation requires Claude Code plugin support.

---

## Verify Installation

Start Claude Code and run:

```
/deep-research test
```

If installed correctly, Claude will begin the research flow.

---

## Directory Structure After Installation

```
your-project/
├── .claude/
│   └── skills/
│       └── deep-research/
│           ├── SKILL.md
│           ├── scripts/
│           │   ├── orchestrator.py
│           │   └── pipelines.py
│           ├── references/
│           └── assets/templates/
│
├── RESEARCH/                    # Created on first use
│   └── [research sessions...]
│
└── prompts/                     # Optional query templates
    ├── query_schema.json
    └── examples/
```

---

## First Research Session

1. Start Claude Code in your project:
   ```bash
   claude
   ```

2. Begin research:
   ```
   /deep-research "Your research topic here"
   ```

3. Follow the prompts:
   - Answer clarification questions
   - Review research plan
   - Wait for completion

4. Find your report:
   ```
   RESEARCH/{topic}_{timestamp}/outputs/
   ```

---

## Troubleshooting

### Skill Not Found

```
Error: Unknown command /deep-research
```

**Solution**: Verify the skill folder exists:
```bash
ls -la .claude/skills/deep-research/SKILL.md
```

### Permission Denied

```
Error: Permission denied creating RESEARCH folder
```

**Solution**: Check write permissions or specify different output path.

### Python Script Errors

```
Error: Python not found
```

**Solution**: Install Python 3.8+ and ensure it's in PATH:
```bash
python3 --version
```

---

## Updating

To update to a new version:

```bash
npx github:fivetaku/deep-research-kit --force
```

Or manually:
```bash
git clone https://github.com/fivetaku/deep-research-kit.git
cp -r deep-research-kit/skills/deep-research ~/.claude/skills/
```

---

## Uninstallation

```bash
# Project-specific
rm -r .claude/skills/deep-research

# Global
rm -r ~/.claude/skills/deep-research
```

> Note: This does not delete research outputs in `RESEARCH/`.
