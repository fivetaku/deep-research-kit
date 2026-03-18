---
name: deep-research-main
description: This skill should be used when a user requests deep research on any topic. Example queries include "/deep-research", "deep research on", "리서치해줘", "딥리서치", "심층 연구", "[주제]에 대해 리서치해줘".
---

# Deep Research Skill

> AI-powered comprehensive research with state management, multi-agent source verification, and structured outputs.

## Trigger Conditions

```
# Primary triggers
- "/deep-research [topic]"
- "/research [topic]"
- "딥리서치 [주제]"
- "심층 연구 [주제]"
- "[주제]에 대해 리서치해줘"
- "[주제] 리서치"
- "deep research on [topic]"

# Resume triggers
- "/deep-research resume [session_id]"
- "/research-resume [session_id]"

# Status triggers
- "/deep-research status"
- "/research-status"
```

---

## WHEN TRIGGERED - EXECUTE IMMEDIATELY

**DO NOT just display this documentation. EXECUTE the research flow immediately.**

### On Trigger Action:

1. **Extract the topic** from user's message
2. **Start Phase 1** - Use `AskUserQuestion` tool for interactive selection

---

## CRITICAL REQUIREMENT

**CALL THE `AskUserQuestion` TOOL IMMEDIATELY.**

DO NOT output text-based questions. INSTEAD, call the AskUserQuestion tool with JSON parameters.

---

### Language Detection
- Detect the language of user's input (topic query)
- Generate ALL question labels and descriptions in the SAME LANGUAGE as user input
- If Korean -> Korean options, If English -> English options, etc.

**EXECUTE:** 아래 JSON으로 AskUserQuestion 도구를 즉시 호출한다 (combine into 1-4 question groups).
Translate all labels/descriptions to match user's language:

**English Example:**
```json
{
  "questions": [
    {
      "question": "What aspects interest you most?",
      "header": "Focus",
      "options": [
        {"label": "Current state & trends", "description": "Latest developments, market status, key players"},
        {"label": "Technical deep-dive", "description": "Architecture, implementation, tech stack"},
        {"label": "Market analysis", "description": "Market size, growth rate, competition"},
        {"label": "All of the above (Recommended)", "description": "Comprehensive research - all aspects"}
      ],
      "multiSelect": false
    },
    {
      "question": "What type of deliverable do you want?",
      "header": "Output",
      "options": [
        {"label": "Comprehensive report (Recommended)", "description": "20-50+ pages, detailed analysis and insights"},
        {"label": "Executive summary", "description": "3-5 pages, key points only"},
        {"label": "Modular documents", "description": "Multiple documents by topic"}
      ],
      "multiSelect": false
    },
    {
      "question": "Who will read this research?",
      "header": "Audience",
      "options": [
        {"label": "Technical team/Developers", "description": "Include technical details"},
        {"label": "Business executives", "description": "Focus on strategic insights"},
        {"label": "Researchers/Academic", "description": "Academic citations and methodology"},
        {"label": "General audience", "description": "Easy explanations and overview"}
      ],
      "multiSelect": false
    },
    {
      "question": "Any source preferences?",
      "header": "Sources",
      "options": [
        {"label": "Academic/Papers", "description": "Peer-reviewed papers, conferences"},
        {"label": "Industry reports", "description": "Gartner, white papers, analyst reports"},
        {"label": "News/Current", "description": "Media, blogs, latest announcements"},
        {"label": "All sources (Recommended)", "description": "All reliable sources"}
      ],
      "multiSelect": false
    }
  ]
}
```

**Korean Example (EXECUTE):**
위 영어 예시와 동일한 4개 질문(Focus, Output, Audience, Sources)을 한국어로 변환하여 전송한다. 아래는 첫 번째 질문의 예시:
```json
{
  "questions": [
    {
      "question": "어떤 측면에 관심이 있으신가요?",
      "header": "Focus",
      "options": [
        {"label": "현재 상태와 트렌드", "description": "최신 동향, 시장 현황, 주요 플레이어"},
        {"label": "기술 심층 분석", "description": "아키텍처, 구현 방법, 기술 스택"},
        {"label": "시장 분석", "description": "시장 규모, 성장률, 경쟁 구도"},
        {"label": "모두 포함 (Recommended)", "description": "종합 리서치 - 모든 측면 분석"}
      ],
      "multiSelect": false
    }
  ]
}
```

3. **After user responds**:
   - Create session folder: `RESEARCH/{topic}_{timestamp}/`
   - Initialize `state.json`
   - Execute Phase 2-7 sequentially
   - Use parallel background agents for searching
   - Deliver final report to `outputs/` folder

---

## The 7-Phase Deep Research Process

> Phase 이름은 코드 내부에서 영어를 사용하며, 사용자 대면 설명은 한국어를 사용합니다.
> 매핑: 질문 정제(Phase 1) → 검색 계획(Phase 2) → 병렬 수집(Phase 3) → 소스 삼각검증(Phase 4) → 지식 합성(Phase 5) → 품질 보증(Phase 6) → 산출물 패키징(Phase 7)

### Phase 1: Question Scoping
- Clarify the research question with the user
- Define output format and success criteria
- Identify constraints and desired tone
- Create unambiguous query with clear parameters

### Phase 2: Retrieval Planning
- Break main question into 3-5 subtopics
- Generate specific search queries per subtopic
- Select appropriate data sources
- Create research plan for user approval
- Use Graph of Thoughts to model research as operations

---

## DATE-AWARE QUERY GENERATION (CRITICAL)

**All search queries MUST include current date context for freshness.**

### Get Today's Date First
Before generating ANY search query, determine today's date from the system context.

### Query Generation Rules

1. **Always append year to queries:**
   - BAD: "AI code assistants market"
   - GOOD: "AI code assistants market 2026"
   - GOOD: "AI code assistants trends February 2026"

2. **Use recency operators:**
   - "after:2025" for Google
   - "since:2025" for news
   - "2025..2026" for date ranges

3. **Add freshness keywords:**
   - "latest", "recent", "current", "new"
   - "[current year] update"

4. **Example transformations:**
   | User Query | Generated Search Query |
   |------------|----------------------|
   | AI 코딩 어시스턴트 | AI 코딩 어시스턴트 2026 최신 동향 |
   | startup trends | startup trends 2026 latest |
   | React vs Vue | React vs Vue 2026 comparison |

5. **For academic/historical research:**
   - Still include current year for "state of" queries
   - Use date ranges: "climate change research 2020-2026"

### Search Query Template
```
[topic] [current_year] [freshness_keyword] [specific_aspect]
```

---

### Phase 3: Iterative Querying
- Execute searches systematically with parallel agents
- Navigate and extract relevant information
  - WebFetch 실패 시 → `tool_strategy.md` Tier 2.5 Fallback 순서대로 시도
  - 우회 성공 시 소스 신뢰도에 `via_fallback` 태그 추가
  - 실패한 URL과 우회 시도 결과를 `sources/failed_urls.txt`에 함께 기록
- Formulate new queries based on findings
- Use multiple search modalities (web, academic, code)

### Phase 4: Source Triangulation
- Compare findings across multiple sources
- Validate claims with cross-references (minimum 2 sources for key claims)
- Handle inconsistencies and note contradictions
- Assess source credibility with A-E ratings

### Phase 5: Knowledge Synthesis
- Structure content logically
- Write comprehensive sections
- Include inline citations for EVERY claim
- Add data visualizations when relevant

### Phase 6: Quality Assurance
- Check for hallucinations and errors
- Verify all citations match content
- Ensure completeness and clarity
- Apply Chain-of-Verification techniques

### Phase 7: Output & Packaging
- Format for optimal readability
- Include executive summary
- Create proper bibliography
- Export in requested format
- Optionally generate interactive website

---

## Multi-Agent Research Strategy

### Agent Deployment (Phase 3)

Deploy 3-5 parallel agents to maximize coverage:

| Agent Type | Count | Focus | Output |
|------------|-------|-------|--------|
| Web Research | 2-3 | Current info, trends, news | Structured summaries with source URLs |
| Academic/Technical | 1-2 | Papers, specs, methodology | Technical analysis with citations |
| Cross-Reference | 1 | Fact-checking, verification | Confidence ratings for key findings |

Launch multiple Agent tool calls in a single response for parallel execution. Each agent receives a focused prompt with specific subtopic and citation requirements.

For detailed agent prompt templates and Graph of Thoughts integration:
`${CLAUDE_PLUGIN_ROOT}/skills/deep-research-main/references/agent_prompts.md`

---

## Tool Usage

Use whichever search and extraction tools are available. Prioritize: MCP tools (Firecrawl, Google Search, Exa) > Built-in tools (WebSearch, WebFetch) > Specialized tools (GitHub search, library docs).

Deploy parallel research agents using the Agent tool with `run_in_background=true` for concurrent subtopic investigation.

For detailed tool strategy and code examples:
`${CLAUDE_PLUGIN_ROOT}/skills/deep-research-main/references/tool_strategy.md`

---

## Citation Requirements

Every factual claim MUST include inline citation.

### Mandatory Standards

1. **Author/Organization** - Who made this claim
2. **Date** - When published
3. **Source Title** - Name of paper, article, or report
4. **URL/DOI** - Direct link to verify
5. **Page Numbers** - For lengthy documents (when applicable)

### Source Quality Ratings

For the complete A-E rating system, red flags, and domain-specific adjustments, refer to the canonical rubric:
`${CLAUDE_PLUGIN_ROOT}/skills/deep-research-main/references/quality_rubric.md`

For detailed citation formatting rules:
`${CLAUDE_PLUGIN_ROOT}/skills/deep-research-main/references/citation_rules.md`

---

## Hallucination Prevention

### Core Strategies

1. **Always ground statements in source material**
   - Never claim without a verifiable source
   - If uncertain, state "Source needed" rather than guessing

2. **Use Chain-of-Verification for critical claims**
   - Generate verification questions
   - Search for answers independently
   - Only finalize when verified

3. **Cross-reference multiple sources**
   - Key findings need 2+ independent sources
   - Note when sources disagree

4. **Explicitly state uncertainty**
   - "According to [source]..." not "Studies show..."
   - Qualify preliminary or contested findings

### Verification Checklist
- [ ] Every claim has inline citation
- [ ] All URLs are accessible
- [ ] No orphan citations
- [ ] Contradictions acknowledged
- [ ] Source quality ratings applied

---

## State Management

### state.json Schema

```json
{
  "session_id": "Topic_Name_20260224_143000",
  "topic": "Research Topic",
  "created_at": "2026-02-24T14:30:00Z",
  "updated_at": "2026-02-24T15:45:00Z",
  "status": "PHASE_3_QUERYING",
  "current_phase": 3,
  "requirements": {
    "focus": ["aspect1", "aspect2"],
    "output_format": "comprehensive_report",
    "scope": {"timeframe": {}, "geography": {}},
    "sources": {"required_types": [], "min_quality": "B"},
    "audience": "executive",
    "special_requirements": []
  },
  "plan": {
    "subtopics": [],
    "search_queries": {},
    "agent_assignments": []
  },
  "progress": {
    "phase_1": "completed",
    "phase_2": "completed",
    "phase_3": "in_progress",
    "phase_4": "pending",
    "phase_5": "pending",
    "phase_6": "pending",
    "phase_7": "pending"
  },
  "sources_count": 0,
  "artifacts": {},
  "errors": []
}
```

### sources.jsonl Schema (one JSON per line)
```json
{"id": "src_001", "url": "https://...", "title": "Article Title", "author": "Author", "date": "2024-06-15", "domain": "nature.com", "type": "academic", "quality_rating": "A", "snippet": "relevant excerpt...", "claims": ["claim1"], "verified": true}
```

For detailed phase input/output contracts:
`${CLAUDE_PLUGIN_ROOT}/skills/deep-research-main/references/phase_contracts.md`

---

## Output Structure

```
RESEARCH/{topic}_{timestamp}/
├── state.json                    # Session state (resumable)
├── README.md                     # Navigation guide
│
├── artifacts/                    # Intermediate outputs
│   ├── research_plan.json
│   ├── agent_results/
│   └── drafts/
│
├── sources/
│   ├── sources.jsonl            # All collected sources
│   ├── bibliography.md          # Formatted citations
│   └── quality_report.md        # Source quality ratings
│
├── outputs/                     # FINAL DELIVERABLES
│   ├── 00_executive_summary.md
│   ├── 01_full_report/
│   │   ├── 01_introduction.md
│   │   ├── 02_current_landscape.md
│   │   ├── 03_challenges.md
│   │   ├── 04_future_outlook.md
│   │   └── 05_conclusions.md
│   ├── 02_end_user_guide/       # (if requested)
│   ├── 03_developer_blueprint/  # (if requested)
│   ├── 04_appendices/
│   └── comparison_data.json
│
└── website/                     # (optional) Visual presentation
    ├── index.html
    ├── styles.css
    └── script.js
```

### Output Templates

Use the templates at `${CLAUDE_PLUGIN_ROOT}/skills/deep-research-main/assets/templates/` for consistent formatting:

| Template | Purpose |
|----------|---------|
| `executive_summary.md` | Executive summary structure |
| `full_report_section.md` | Individual report section template |
| `bibliography.md` | Bibliography with quality distribution |
| `readme_research.md` | Research session README/navigation |
| `website_template.html` | Interactive web presentation |

---

## Structured Query Support

For precise research control, accept structured JSON queries following the schema at:
`${CLAUDE_PLUGIN_ROOT}/skills/deep-research-main/references/query_schema.json`

When a user provides a JSON object as input, parse it according to the schema and skip Phase 1 (Question Scoping) since requirements are already defined.

Example queries are available at:
`${CLAUDE_PLUGIN_ROOT}/skills/deep-research-main/examples/`

---

## Resume Protocol

When resume is triggered:

1. List available sessions: `RESEARCH/*/state.json`
2. Load selected session's `state.json`
3. Check `progress` object for last completed phase
4. Resume from next pending phase
5. Continue execution loop

```python
for phase_num in range(1, 8):
    phase_key = f"phase_{phase_num}"
    if state["progress"][phase_key] == "in_progress":
        resume_phase(phase_num)
        break
    elif state["progress"][phase_key] == "pending":
        start_phase(phase_num)
        break
```

---

## Error Handling

### Phase Failures
1. Log error to `state.json` errors array
2. Mark phase as `failed` in progress
3. Notify user with details
4. Offer: Retry / Skip / Abort

### Network Failures
- Retry up to 3 times with backoff
- If still failing → Execute Tier 2.5 Fallback Strategy (`tool_strategy.md` 참조)
  - 모바일 UA curl → RSS 피드 → OGP 메타태그 → Google 캐시/Wayback → curl_cffi → Playwright MCP
- Log failed URLs + fallback attempt results to `sources/failed_urls.txt`
- Continue with available sources (including fallback-retrieved content)

### Token Limits
- Split long documents into chunks
- Save intermediate results frequently
- Use summarization for very long sources

---

## Quality Checklist (Before Completion)

- [ ] Every claim has a verifiable source
- [ ] Multiple sources corroborate key findings
- [ ] Contradictions are acknowledged and explained
- [ ] Sources are recent and authoritative
- [ ] No hallucinations or unsupported claims
- [ ] Clear logical flow from evidence to conclusions
- [ ] Proper citation format throughout
- [ ] Executive summary reflects full content
- [ ] Bibliography is complete
- [ ] All background agents completed and results collected

---

## Scripts and Utilities

State management scripts are available at:
`${CLAUDE_PLUGIN_ROOT}/skills/deep-research-main/scripts/`

| Script | Purpose |
|--------|---------|
| `orchestrator.py` | Research state machine controller - session creation, phase management, source tracking |
| `pipelines.py` | Pipeline definitions - agent prompts, subtopic decomposition, synthesis prompts |

These can be executed via Bash to initialize sessions or manage state programmatically.

---

## References

For detailed documentation on specific aspects:

| Reference | Location |
|-----------|----------|
| Citation formatting rules | `${CLAUDE_PLUGIN_ROOT}/skills/deep-research-main/references/citation_rules.md` |
| Phase input/output contracts | `${CLAUDE_PLUGIN_ROOT}/skills/deep-research-main/references/phase_contracts.md` |
| Source quality rubric | `${CLAUDE_PLUGIN_ROOT}/skills/deep-research-main/references/quality_rubric.md` |
| Agent prompt templates & GoT | `${CLAUDE_PLUGIN_ROOT}/skills/deep-research-main/references/agent_prompts.md` |
| Tool strategy & code examples | `${CLAUDE_PLUGIN_ROOT}/skills/deep-research-main/references/tool_strategy.md` |
| Structured query schema | `${CLAUDE_PLUGIN_ROOT}/skills/deep-research-main/references/query_schema.json` |
| Query builder skill | `${CLAUDE_PLUGIN_ROOT}/skills/deep-research-query/SKILL.md` |
