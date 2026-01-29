# Deep Research Kit

**[한국어 버전 (Korean)](README.ko.md)**

> AI-powered deep research skill for Claude Code - comprehensive research with state management, source verification, and structured outputs.

Transform vague research questions into comprehensive, well-cited reports using Claude's agentic capabilities.

## Demo

```
User: /deep-research "Impact of AI code assistants on developer productivity 2024"

Claude:
1. Asks clarification questions (scope, audience, format)
2. Creates research plan with subtopics
3. Deploys parallel agents to search and collect sources
4. Cross-verifies findings across multiple sources
5. Generates comprehensive report with citations

Output: RESEARCH/AI_Code_Assistants_20260129_143000/outputs/
├── 00_executive_summary.md
├── 01_full_report/
└── sources/bibliography.md
```

## Setup

### Install via npx (Recommended)

```bash
npx github:fivetaku/deep-research-kit
```

This copies the skill files to `.claude/skills/deep-research/`.

**Options:**
```bash
# Install to current project (default if .claude/ exists)
npx github:fivetaku/deep-research-kit --project

# Install globally to ~/.claude/skills/
npx github:fivetaku/deep-research-kit --global
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/fivetaku/deep-research-kit.git

# Copy to your project
cp -r deep-research-kit/plugins/deep-research/skills/deep-research YOUR_PROJECT/.claude/skills/

# Or copy to home directory (global)
cp -r deep-research-kit/plugins/deep-research/skills/deep-research ~/.claude/skills/
```

### Uninstall

```bash
rm -rf ~/.claude/skills/deep-research
# or
rm -rf .claude/skills/deep-research
```

## Usage

### Start New Research

```
/deep-research "your research topic"
```

### With Structured Query (Advanced)

```
/deep-research {
  "task": {"title": "AI Healthcare Study", "objective": "...", "type": "analytical"},
  "context": {"audience": "executive", ...},
  "questions": {"primary": "...", "secondary": [...]},
  "constraints": {"timeframe": {...}, "sources": {...}},
  "output": {"format": "comprehensive_report", ...}
}
```

### Resume Previous Session

```
/research-status          # List all sessions
/research-resume <id>     # Continue from last checkpoint
```

### Interactive Query Builder

```
/research-query           # Guided query construction
```

## Output Location

All research outputs are saved to:

```
RESEARCH/{topic}_{timestamp}/
├── state.json              # Session state (resumable)
├── README.md               # Navigation guide
│
├── outputs/                # <<< FINAL DELIVERABLES
│   ├── 00_executive_summary.md
│   ├── 01_full_report/
│   │   ├── 01_introduction.md
│   │   ├── 02_methodology.md
│   │   ├── 03_findings.md
│   │   └── 04_conclusions.md
│   └── 02_appendices/
│
├── sources/
│   ├── sources.jsonl       # Raw source data
│   ├── bibliography.md     # Formatted citations
│   └── quality_report.md   # Source quality analysis
│
└── website/                # Optional HTML visualization
    └── index.html
```

## The 7-Phase Pipeline

| Phase | Name | Description |
|-------|------|-------------|
| 1 | **Question Scoping** | Clarify research question, define requirements |
| 2 | **Retrieval Planning** | Decompose into subtopics, generate search queries |
| 3 | **Iterative Querying** | Execute parallel searches, collect sources |
| 4 | **Source Triangulation** | Cross-reference, validate with 2+ sources |
| 5 | **Knowledge Synthesis** | Merge findings, create draft with citations |
| 6 | **Quality Assurance** | Check hallucinations, verify all citations |
| 7 | **Output & Packaging** | Generate final deliverables |

## Source Quality Grades

| Grade | Description | Examples |
|-------|-------------|----------|
| **A** | Peer-reviewed, systematic reviews | Nature, Lancet, IEEE |
| **B** | Official docs, guidelines | FDA, W3C, official docs |
| **C** | Expert opinion, reports | Gartner, conferences |
| **D** | Preliminary, preprints | arXiv, white papers |
| **E** | Anecdotal, speculative | Blogs, social media |

## Project Structure

```
deep-research-kit/
├── bin/
│   └── install.js              # npx installer
├── plugins/
│   └── deep-research/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── SKILL.md
│       └── skills/
│           └── deep-research/
│               ├── SKILL.md         # Skill definition
│               ├── scripts/
│               │   ├── orchestrator.py
│               │   └── pipelines.py
│               ├── references/
│               │   ├── quality_rubric.md
│               │   ├── citation_rules.md
│               │   └── phase_contracts.md
│               └── assets/templates/
│                   ├── executive_summary.md
│                   ├── bibliography.md
│                   └── website_template.html
├── package.json
├── README.md
└── README.ko.md
```

## Query Generator

Transform vague ideas into structured research queries:

1. Open any LLM (ChatGPT, Claude, Gemini)
2. Set system prompt to `prompts/query_generator_system.md`
3. Describe your research topic
4. Answer clarification questions
5. Get structured JSON query
6. Use with `/deep-research [JSON]`

## Why Use This Kit?

**Claude Code에서 딥리서치를 수행하고 결과를 로컬에 저장합니다.**

### Core Benefits

| Benefit | Description |
|---------|-------------|
| **Local Storage** | 모든 리서치 결과가 로컬 파일로 저장 - 클라우드 의존 없음 |
| **Structured Output** | 체계적인 폴더 구조 (executive summary, full report, sources) |
| **Resumable Sessions** | `state.json`으로 언제든 중단/재개 가능 |
| **Source Quality Grading** | A-E 등급으로 소스 신뢰도 평가 |
| **Date-Aware Queries** | 자동으로 현재 연도 삽입하여 최신 정보 검색 |
| **Full Customization** | JSON 스키마로 리서치 범위, 형식, 소스 유형 지정 |

### What You Can Do With It

```
RESEARCH/{topic}_{timestamp}/
├── outputs/           → 최종 보고서 (markdown)
├── sources/           → 원본 소스 데이터
└── website/           → HTML 시각화
```

- 📄 보고서를 Notion, Obsidian, 블로그에 바로 복사
- 🔍 소스 데이터로 추가 분석 및 fact-checking
- 🌐 HTML 결과물로 팀과 공유
- 🔄 이전 리서치 세션 이어서 진행
- 🛠️ 다른 Claude Code 작업과 연계 (코드 생성, 문서 작성 등)

## Tips for Best Results

1. **Be Specific** - "AI in healthcare radiology 2024" > "AI in healthcare"
2. **Define Audience** - Technical vs executive changes depth and tone
3. **Set Time Bounds** - "Since 2023" prevents outdated sources
4. **Specify Source Types** - Academic-only vs including industry reports
5. **Use JSON Queries** - For reproducible, precise research

## Troubleshooting

### Research Taking Too Long
- Narrow scope (fewer subtopics)
- Reduce source requirements
- Use `min_quality: "C"` instead of "B"

### Missing Sources
- Broaden search terms
- Include more source types
- Extend timeframe

### Resume Not Working
- Check `RESEARCH/*/state.json` exists
- Verify session_id spelling

## Requirements

- **Claude Code** with agentic capabilities
- **Python 3.8+** (for orchestrator script)
- **Node.js 16+** (for npx installation)

## Contributing

Contributions welcome! Feel free to:
- Add new output templates
- Improve search strategies
- Enhance verification methods
- Add language support

## License

MIT License - see [LICENSE](LICENSE) for details.

## Credits

- Inspired by OpenAI and Google deep research methodologies
- Built for [Claude Code](https://claude.ai/code)
