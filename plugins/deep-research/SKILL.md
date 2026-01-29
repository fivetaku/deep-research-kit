---
name: deep-research
description: AI-powered deep research skill. Use when users say "/deep-research", "deep research on", "리서치해줘", or want comprehensive research with citations.
---

# Deep Research Skill

> AI-powered comprehensive research with state management, source verification, and structured outputs.

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
- "/research-resume [session_id]"
- "/research-status"
```

---

## WHEN TRIGGERED - EXECUTE IMMEDIATELY

**DO NOT just display this documentation. EXECUTE the research flow immediately.**

### On Trigger Action:

1. **Extract the topic** from user's message
2. **Start Phase 1** - Use `AskUserQuestion` tool for interactive selection:

---
## ⚠️ CRITICAL REQUIREMENT - READ THIS ⚠️

**YOU MUST CALL THE `AskUserQuestion` TOOL IMMEDIATELY.**

❌ DO NOT output text-based questions like:
```
1. Specific Focus: 어떤 측면에...
2. Output Format: 어떤 형태로...
```

✅ INSTEAD, call the AskUserQuestion tool with JSON parameters.

**THIS IS MANDATORY. VIOLATION OF THIS RULE IS NOT ACCEPTABLE.**

---

### Language Detection
- Detect the language of user's input (topic query)
- Generate ALL question labels and descriptions in the SAME LANGUAGE as user input
- If Korean → Korean options, If English → English options, etc.

Use `AskUserQuestion` with these questions (combine into 1-4 question groups).
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

**Korean Example:**
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

### Phase 3: Iterative Querying
- Execute searches systematically with parallel agents
- Navigate and extract relevant information
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

---

## Multi-Agent Research Strategy

### Agent Deployment (Phase 3)

Deploy 3-5 parallel agents to maximize coverage:

**Agent Type 1: Web Research Agents** (2-3 agents)
```
Focus: Current information, trends, news
Objective: Gather recent developments and real-world data
Output: Structured summaries with source URLs
```

**Agent Type 2: Academic/Technical Agent** (1-2 agents)
```
Focus: Research papers, technical specifications
Objective: Find theoretical foundations and methodologies
Output: Technical analysis with proper citations
```

**Agent Type 3: Cross-Reference Agent** (1 agent)
```
Focus: Fact-checking and verification
Objective: Validate claims across sources
Output: Confidence ratings for key findings
```

### Agent Prompt Templates

**General Research Agent:**
```
Research [specific aspect] of [main topic].

Tools to use:
1. mcp_google_search for web search
2. mcp_websearch_web_search_exa for deep search
3. mcp_webfetch to extract content from URLs

Focus on finding:
- Recent information (prioritize last 2 years)
- Authoritative sources
- Specific data/statistics
- Multiple perspectives

For EVERY factual claim, provide:
- Direct quote or data point
- Source URL
- Author/organization
- Publication date
- Confidence rating (High/Medium/Low)

Return structured findings with all source URLs.
```

**Technical Research Agent:**
```
Find technical/academic information about [topic].

Tools to use:
1. mcp_google_search for academic papers
2. mcp_context7_query_docs for library docs
3. mcp_grep_app_searchGitHub for code examples

Look for:
- Peer-reviewed papers
- Technical specifications
- Methodologies and frameworks
- Scientific evidence

Include proper academic citations with DOI/URLs.
```

**Verification Agent:**
```
Verify the following claims about [topic]:
[List key claims to verify]

Use multiple search queries to find:
- Supporting evidence
- Contradicting information
- Original sources

Rate confidence: High/Medium/Low for each claim.
Explain any contradictions found.
Never confirm without sources.
```

### Agent Deployment Pattern

```python
# Deploy parallel agents for subtopics
background_task(agent="explore", prompt="Research current state of [subtopic1]...")
background_task(agent="explore", prompt="Research challenges in [subtopic2]...")
background_task(agent="librarian", prompt="Find official documentation for [subtopic3]...")
background_task(agent="librarian", prompt="Find academic papers on [subtopic4]...")
background_task(agent="explore", prompt="Verify key claims: [list claims]...")

# Continue immediately, collect results later with:
# background_output(task_id="...")

# Cancel all before completion:
# background_cancel(all=True)
```

---

## Graph of Thoughts Integration

The research process uses Graph of Thoughts (GoT) for complex reasoning:

1. **Modeling Research as Graph Operations**: Each research step becomes a node
2. **Parallel Processing**: Multiple research paths explored simultaneously
3. **Scoring & Optimization**: Information quality scored and optimized
4. **Backtracking**: Poor research paths abandoned for better alternatives

### GoT Operations:
- **Generate**: Create search queries and hypotheses
- **Score**: Evaluate information quality and relevance
- **GroundTruth**: Verify facts against authoritative sources
- **Aggregate**: Combine findings from multiple sources
- **Improve**: Refine research questions based on findings

---

## Tool Usage

### Primary Search Tools
```python
# Google Search with AI analysis
mcp_google_search(query="...", thinking=True)

# Exa deep search (comprehensive)
mcp_websearch_web_search_exa(query="...", type="deep", numResults=10)

# Content extraction from URL
mcp_webfetch(url="...", format="markdown")
```

### Specialized Tools
```python
# GitHub code examples
mcp_grep_app_searchGitHub(query="...", language=["Python", "TypeScript"])

# Library documentation
mcp_context7_resolve_library_id(libraryName="react", query="hooks")
mcp_context7_query_docs(libraryId="/facebook/react", query="useEffect")
```

### Background Agents
```python
# Fire parallel research agents
task_id = mcp_background_task(
    agent="explore",  # or "librarian"
    description="Research subtopic",
    prompt="Detailed research instructions..."
)

# Collect results when needed
result = mcp_background_output(task_id=task_id)

# Cancel all before final answer
mcp_background_cancel(all=True)
```

### File Operations
```python
mcp_write(filePath="RESEARCH/.../file.md", content="...")
mcp_read(filePath="RESEARCH/.../state.json")
mcp_glob(pattern="RESEARCH/**/*.md")
```

---

## Citation Requirements

### Mandatory Standards

**Every factual claim must include:**
1. **Author/Organization** - Who made this claim
2. **Date** - When published
3. **Source Title** - Name of paper, article, or report
4. **URL/DOI** - Direct link to verify
5. **Page Numbers** - For lengthy documents (when applicable)

### Citation Formats

**Academic Papers:**
```
(Author et al., Year, p. XX)
Full: Smith, J., Johnson, K., & Lee, M. (2023). "Title." Journal, 45(3), 140-156. https://doi.org/xxx
```

**Web Sources:**
```
(Organization, Year, Section)
Full: NIH. (2024). "Treatment Guidelines." https://www.nih.gov/page
```

**Direct Quotes:**
```
"Exact quote from source" (Author, Year, p. XX)
```

### Source Quality Ratings

| Grade | Description | Examples |
|-------|-------------|----------|
| **A** | Peer-reviewed, systematic reviews, meta-analyses | Nature, Lancet, IEEE |
| **B** | Official docs, clinical guidelines, cohort studies | FDA, W3C, WHO |
| **C** | Expert opinion, case reports, industry reports | Gartner, conferences |
| **D** | Preliminary research, preprints, white papers | arXiv, company blogs |
| **E** | Anecdotal, theoretical, speculative | Social media, forums |

### Red Flags (Unreliable Sources)
- No author attribution
- Missing publication dates
- Broken or suspicious URLs
- Claims without data
- Conflicts of interest not disclosed
- Predatory journals
- Retracted papers

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
  "session_id": "Topic_Name_20260129_143000",
  "topic": "Research Topic",
  "created_at": "2026-01-29T14:30:00Z",
  "updated_at": "2026-01-29T15:45:00Z",
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
│   ├── 02_appendices/
│   └── comparison_data.json
│
└── website/                     # (optional) Visual presentation
    ├── index.html
    ├── styles.css
    └── script.js
```

---

## Resume Protocol

When `/research-resume [session_id]` is called:

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
- Log failed URLs to `sources/failed_urls.txt`
- Continue with available sources

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
- [ ] All background agents cancelled

---

## Example Interaction Flow

```
User: "/deep-research AI 코드 어시스턴트가 개발자 생산성에 미치는 영향"

Assistant: "AI 코드 어시스턴트의 생산성 영향에 대해 딥리서치를 진행하겠습니다.

1. **Specific Focus**: 어떤 측면에 관심이 있으신가요?
   - 생산성 측정 메트릭
   - 도구별 비교 (Copilot, Cursor, Codeium 등)
   - 도입 장벽과 과제
   - 모두 포함

2. **Output Format**: 어떤 형태로 드릴까요?
   - 종합 리포트 (20+ 페이지)
   - 요약본 (3-5 페이지)

3. **Scope**: 제약 조건이 있나요?
   - 시간: 2022년 이후?
   - 지역: 글로벌?

4. **Audience**: 누가 읽을 건가요?
   - 엔지니어링 리더십

아니면 '진행해'라고 하시면 기본 설정으로 시작합니다."

User: "진행해"
```
