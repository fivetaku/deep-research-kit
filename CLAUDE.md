# Deep Research Kit

This workspace contains the Deep Research skill for Claude Code.

## Quick Start

```
/deep-research "your research topic"
```

## What It Does

Deep Research is an AI-driven comprehensive research system that:
- Conducts multi-step research autonomously
- Searches, reads, and analyzes information across the web
- Cross-verifies facts with multiple sources
- Produces detailed reports with explicit citations

## The 7-Phase Pipeline

1. **Question Scoping** - Clarify research question and requirements
2. **Retrieval Planning** - Decompose into subtopics, generate search queries
3. **Iterative Querying** - Execute searches with parallel agents
4. **Source Triangulation** - Cross-reference and validate findings
5. **Knowledge Synthesis** - Merge information into coherent draft
6. **Quality Assurance** - Check for hallucinations, verify citations
7. **Output & Packaging** - Generate final deliverables

## Output Location

All research outputs are saved to:
```
RESEARCH/{topic}_{timestamp}/outputs/
```

## Commands

| Command | Description |
|---------|-------------|
| `/deep-research [topic]` | Start new research |
| `/deep-research [JSON]` | Start with structured query |
| `/research-resume [id]` | Resume previous session |
| `/research-status` | List all sessions |
| `/research-query` | Interactive query builder |

## Source Quality Grades

| Grade | Description |
|-------|-------------|
| A | Peer-reviewed, systematic reviews |
| B | Official docs, guidelines |
| C | Expert opinion, reports |
| D | Preliminary, preprints |
| E | Anecdotal, speculative |

## Key Rules

1. **Every claim needs a citation** - No unsupported statements
2. **Cross-reference critical findings** - Minimum 2 sources for key claims
3. **Note contradictions** - When sources disagree, acknowledge it
4. **Prefer recent sources** - Prioritize 2024-2025 for fast-moving topics

## Structured Query (Advanced)

For precise control, provide a JSON query following the schema in `prompts/query_schema.json`.

See examples in `prompts/examples/` folder.

## Examples

See `examples/` folder for sample research outputs including:
- AI Detection Research (comparison with OpenAI, Gemini, Perplexity, Manus)
- Website visualization examples
