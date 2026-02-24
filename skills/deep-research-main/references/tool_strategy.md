# Adaptive Tool Strategy

Use whichever web search and content extraction tools are available in the current environment. Prioritize in this order:

## Tier 1 - MCP Tools (if available)

```python
# Firecrawl (preferred if installed)
firecrawl_search(query="...", limit=10)
firecrawl_scrape(url="...")

# Google Search MCP
mcp_google_search(query="...", thinking=True)

# Exa deep search
mcp_websearch_web_search_exa(query="...", type="deep", numResults=10)
```

## Tier 2 - Built-in Tools

```python
# Web search (always available)
WebSearch(query="...")

# Content extraction from URL
WebFetch(url="...", prompt="Extract key findings and data")
```

## Tier 3 - Specialized Tools (if available)

```python
# GitHub code examples
mcp_grep_app_searchGitHub(query="...", language=["Python", "TypeScript"])

# Library documentation
mcp_context7_resolve_library_id(libraryName="react", query="hooks")
mcp_context7_query_docs(libraryId="/facebook/react", query="useEffect")
```

## Background Agents for Parallel Research

```python
# Deploy parallel research agents using Task tool
Task(
    subagent_type="Explore",
    description="Research subtopic",
    prompt="Detailed research instructions...",
    run_in_background=True
)

# Or use general-purpose agent for broader research
Task(
    subagent_type="general-purpose",
    description="Deep research on subtopic",
    prompt="...",
    run_in_background=True
)
```

## File Operations

```python
Write(file_path="RESEARCH/.../file.md", content="...")
Read(file_path="RESEARCH/.../state.json")
Glob(pattern="RESEARCH/**/*.md")
```
