---
name: deep-research
description: "AI 딥리서치 -- 멀티에이전트 기반 종합 리서치 시스템"
argument-hint: "[topic|resume|status|query]"
allowed-tools:
  - Task
  - WebSearch
  - WebFetch
  - Read
  - Write
  - Glob
  - Bash
  - Grep
---

# /deep-research Command

AI-powered deep research system that conducts multi-step research autonomously with source verification and structured outputs.

## Parse Arguments

Inspect `$ARGUMENTS` to determine the action:

| Argument Pattern | Action | Skill |
|-----------------|--------|-------|
| `resume [session_id]` | Resume a previous research session | deep-research-main |
| `status` | List all research sessions and their progress | deep-research-main |
| `query` | Launch interactive query builder | deep-research-query |
| `[any other text]` | Start new research on the given topic | deep-research-main |
| (no argument) | Show interactive menu via AskUserQuestion | See below |

## No Argument Provided

When no argument is provided, present the following interactive menu using `AskUserQuestion`:

```json
{
  "questions": [
    {
      "question": "What would you like to do?",
      "header": "Action",
      "options": [
        {"label": "New Research", "description": "Start a new deep research on any topic"},
        {"label": "Resume Session", "description": "Continue a previously interrupted research"},
        {"label": "Session Status", "description": "View all research sessions and their progress"},
        {"label": "Query Builder", "description": "Create a structured research query interactively"}
      ],
      "multiSelect": false
    }
  ]
}
```

After user selection:
- **New Research** → Ask for topic, then invoke deep-research-main skill
- **Resume Session** → List sessions from `RESEARCH/*/state.json`, let user pick, then invoke deep-research-main resume flow
- **Session Status** → List all sessions with progress summary
- **Query Builder** → Invoke deep-research-query skill

## Execute

Once the action is determined, follow the corresponding skill's execution flow.

Skill content is located at:
- `${CLAUDE_PLUGIN_ROOT}/skills/deep-research-main/SKILL.md` — Main research pipeline
- `${CLAUDE_PLUGIN_ROOT}/skills/deep-research-query/SKILL.md` — Interactive query builder
