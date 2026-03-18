#!/usr/bin/env python3
"""
Deep Research Pipeline Definitions
"""

from typing import Dict, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


def _current_year() -> int:
    return datetime.now().year


def _date_range_recent() -> str:
    year = _current_year()
    return f"{year - 1}-{year}"


def _date_range_broad() -> str:
    year = _current_year()
    return f"{year - 2}-{year}"


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
- What exists today ({date_range_recent})
- Key players and solutions
- Market size and adoption rates
- Real-world implementations

Use available search and extraction tools (MCP or built-in) to find:

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

Prioritize recent sources ({date_range_recent}).
Cite all claims with full source information.

Return structured findings with timeline indicators.
""",
    "librarian_docs": """
Find OFFICIAL DOCUMENTATION and TECHNICAL RESOURCES for {subtopic}

Use available search tools (library docs, code search, web search) to find:

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

Prioritize recent publications ({date_range_broad}).
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
    date_ctx = {
        "date_range_recent": _date_range_recent(),
        "date_range_broad": _date_range_broad(),
    }

    for subtopic in subtopics:
        tasks.append(
            AgentTask(
                agent_type=AgentType.EXPLORE,
                description=f"Current state of {subtopic}",
                prompt=AGENT_PROMPTS["explore_current_state"].format(
                    subtopic=subtopic, topic=topic, **date_ctx
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
                subtopic="overall topic", topic=topic, **date_ctx
            ),
            subtopic="future",
            expected_output="Future predictions with timeline",
        )
    )

    return tasks


def get_agent_prompt(name: str, **kwargs) -> str:
    """Get an agent prompt with date context automatically injected."""
    date_ctx = {
        "date_range_recent": _date_range_recent(),
        "date_range_broad": _date_range_broad(),
    }
    merged = {**date_ctx, **kwargs}
    return AGENT_PROMPTS[name].format(**merged)


def get_verification_prompt(claims: List[str], subtopic: str) -> str:
    claims_text = "\n".join(f"- {claim}" for claim in claims)
    return get_agent_prompt("verification", subtopic=subtopic, claims_to_verify=claims_text)


def get_synthesis_prompt(subtopic: str, findings: str) -> str:
    return SYNTHESIS_PROMPT.format(subtopic=subtopic, findings=findings)
