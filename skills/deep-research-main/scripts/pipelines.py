#!/usr/bin/env python3
"""
Deep Research Pipeline Definitions
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class AgentType(Enum):
    EXPLORE = "explore"
    LIBRARIAN = "librarian"
    GENERAL = "general"


@dataclass
class SearchQuery:
    query: str
    subtopic: str
    priority: int = 1
    tools: List[str] = field(default_factory=lambda: ["google_search"])


@dataclass
class AgentTask:
    agent_type: AgentType
    description: str
    prompt: str
    subtopic: str
    expected_output: str


@dataclass
class PipelineConfig:
    max_sources_per_subtopic: int = 10
    min_sources_for_triangulation: int = 2
    quality_threshold: str = "C"
    max_parallel_agents: int = 5
    search_timeout_seconds: int = 60


CLARIFICATION_QUESTIONS = """
I'll help you conduct deep research on **{topic}**. Let me ask a few questions to ensure I deliver exactly what you need:

1. **Specific Focus**: What aspects of {topic} interest you most?
   - Current state and trends
   - Technical deep-dive
   - Market analysis
   - Future predictions
   - All of the above

2. **Output Format**: What type of deliverable would be most useful?
   - Comprehensive report (20-50+ pages)
   - Executive summary (3-5 pages)
   - Modular folder structure with multiple documents
   - Data analysis with visualizations

3. **Scope**: Any specific constraints?
   - Geographic focus (Global, US, Europe, Asia, etc.)
   - Time period (Current, last N years, future projections)
   - Industries or domains to focus on
   - What should be EXCLUDED?

4. **Sources**: Source preferences?
   - Academic/peer-reviewed only
   - Industry reports and white papers
   - News and current events
   - Official documentation
   - Any sources to avoid?

5. **Audience**: Who will read this research?
   - Technical team
   - Business executives
   - Researchers/academics
   - General audience

6. **Special Requirements**:
   - Specific data or statistics needed?
   - Comparison frameworks?
   - Code examples or technical blueprints?
   - Visualizations (charts, diagrams)?
"""


SUBTOPIC_DECOMPOSITION_PROMPT = """
Based on the research topic "{topic}" and requirements:
{requirements}

Decompose this into 3-5 distinct subtopics for parallel research.

For each subtopic, provide:
1. Subtopic name
2. Key questions to answer
3. Suggested search queries (3-5 per subtopic)
4. Recommended source types
5. Expected output format

Return as structured JSON.
"""


AGENT_PROMPTS = {
    "explore_current_state": """
Research the CURRENT STATE of {subtopic} for topic: {topic}

Focus on:
- What exists today (2024-2025)
- Key players and solutions
- Market size and adoption rates
- Real-world implementations

Use these tools:
1. mcp_google_search for recent news and reports
2. mcp_websearch for deep web search
3. mcp_webfetch to extract content from URLs

For EVERY factual claim, provide:
- Direct quote or data point
- Source URL
- Author/organization
- Publication date
- Confidence rating (High/Medium/Low)

Return structured findings with full citations.
""",
    "explore_challenges": """
Research the CHALLENGES AND LIMITATIONS of {subtopic} for topic: {topic}

Focus on:
- Technical limitations
- Known failure modes
- Adoption barriers
- Criticisms and controversies
- Ethical concerns

For EVERY claim, cite the source with URL, author, and date.

Return structured findings organized by challenge type.
""",
    "explore_future": """
Research FUTURE DEVELOPMENTS of {subtopic} for topic: {topic}

Focus on:
- Emerging technologies (next 1-3 years)
- Research breakthroughs
- Industry roadmaps
- Expert predictions
- Potential disruptions

Prioritize recent sources (2024-2025).
Cite all claims with full source information.

Return structured findings with timeline indicators.
""",
    "librarian_docs": """
Find OFFICIAL DOCUMENTATION and TECHNICAL RESOURCES for {subtopic}

Use:
1. mcp_context7 for library documentation
2. mcp_grep_app for GitHub code examples
3. mcp_google_search for official specs

Focus on:
- Official documentation
- API references
- Technical specifications
- Standards documents (ISO, IEEE, etc.)
- Implementation guides

Return structured list with URLs and descriptions.
""",
    "librarian_academic": """
Find ACADEMIC AND RESEARCH sources for {subtopic}

Search for:
- Peer-reviewed papers
- Conference proceedings
- Technical reports
- Systematic reviews
- Meta-analyses

Include:
- Title, authors, year
- Journal/conference name
- DOI or URL
- Key findings summary
- Relevance score

Prioritize recent publications (2023-2025).
""",
    "verification": """
VERIFY the following claims about {subtopic}:

{claims_to_verify}

For each claim:
1. Search for supporting evidence from independent sources
2. Search for contradicting information
3. Check the original source quality
4. Rate confidence: High/Medium/Low/Unverifiable

Return verification report with:
- Claim
- Verification status
- Supporting sources
- Contradicting sources (if any)
- Final confidence rating
""",
}


SYNTHESIS_PROMPT = """
Synthesize the following research findings into a coherent section on {subtopic}:

{findings}

Requirements:
1. Logical structure with clear headings
2. Every factual claim must have inline citation
3. Note any contradictions between sources
4. Highlight confidence levels for key claims
5. Include data visualizations where appropriate

Citation format: (Author, Year) with full reference in bibliography

Output format:
- Introduction to subtopic
- Key findings (with citations)
- Data/statistics (with sources)
- Challenges and limitations
- Future outlook
- Summary
"""


QA_CHECKLIST = """
## Quality Assurance Checklist

### Citation Verification
- [ ] Every factual claim has a source citation
- [ ] All URLs are accessible and valid
- [ ] Citation format is consistent throughout
- [ ] No broken or dead links

### Content Quality
- [ ] No hallucinated facts or statistics
- [ ] Multiple sources corroborate key findings
- [ ] Contradictions are noted and explained
- [ ] Sources are recent (within scope timeframe)
- [ ] Source quality ratings applied (A-E)

### Completeness
- [ ] All subtopics covered adequately
- [ ] Executive summary reflects full content
- [ ] Bibliography is complete
- [ ] No obvious gaps in coverage

### Structure
- [ ] Logical flow between sections
- [ ] Consistent formatting
- [ ] Table of contents accurate
- [ ] Headings hierarchy correct

### Special Requirements
- [ ] Audience-appropriate language
- [ ] Requested visualizations included
- [ ] Geographic scope honored
- [ ] Time period constraints met
"""


SOURCE_QUALITY_RUBRIC = """
## Source Quality Rating System

### A - Highest Quality
- Peer-reviewed systematic reviews and meta-analyses
- Randomized controlled trials
- Official government/regulatory publications
- Major institution research reports

### B - High Quality  
- Peer-reviewed original research
- Official industry standards documents
- Established organization white papers
- Clinical/practice guidelines

### C - Moderate Quality
- Expert opinion pieces
- Conference presentations
- Case studies and reports
- Reputable news analysis

### D - Lower Quality
- Preprints (not peer-reviewed)
- Blog posts from domain experts
- Conference abstracts
- Industry press releases

### E - Use with Caution
- Anonymous sources
- Opinion without evidence
- Outdated information (>3 years for fast-moving fields)
- Sources with clear bias/conflicts
"""


def generate_research_plan(topic: str, requirements: Dict) -> Dict:
    return {
        "topic": topic,
        "requirements": requirements,
        "subtopics": [],
        "search_queries": {},
        "agent_assignments": [],
        "estimated_sources": 0,
        "estimated_time_minutes": 0,
    }


def create_agent_tasks(subtopics: List[str], topic: str) -> List[AgentTask]:
    tasks = []

    for subtopic in subtopics:
        tasks.append(
            AgentTask(
                agent_type=AgentType.EXPLORE,
                description=f"Current state of {subtopic}",
                prompt=AGENT_PROMPTS["explore_current_state"].format(
                    subtopic=subtopic, topic=topic
                ),
                subtopic=subtopic,
                expected_output="Structured findings with citations",
            )
        )

        tasks.append(
            AgentTask(
                agent_type=AgentType.EXPLORE,
                description=f"Challenges in {subtopic}",
                prompt=AGENT_PROMPTS["explore_challenges"].format(
                    subtopic=subtopic, topic=topic
                ),
                subtopic=subtopic,
                expected_output="Challenge analysis with sources",
            )
        )

        tasks.append(
            AgentTask(
                agent_type=AgentType.LIBRARIAN,
                description=f"Documentation for {subtopic}",
                prompt=AGENT_PROMPTS["librarian_docs"].format(subtopic=subtopic),
                subtopic=subtopic,
                expected_output="Documentation links and summaries",
            )
        )

    tasks.append(
        AgentTask(
            agent_type=AgentType.EXPLORE,
            description=f"Future developments for {topic}",
            prompt=AGENT_PROMPTS["explore_future"].format(
                subtopic="overall topic", topic=topic
            ),
            subtopic="future",
            expected_output="Future predictions with timeline",
        )
    )

    return tasks


def get_verification_prompt(claims: List[str], subtopic: str) -> str:
    claims_text = "\n".join(f"- {claim}" for claim in claims)
    return AGENT_PROMPTS["verification"].format(
        subtopic=subtopic, claims_to_verify=claims_text
    )


def get_synthesis_prompt(subtopic: str, findings: str) -> str:
    return SYNTHESIS_PROMPT.format(subtopic=subtopic, findings=findings)
