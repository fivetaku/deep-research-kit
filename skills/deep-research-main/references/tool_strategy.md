# Adaptive Tool Strategy

Use whichever web search and content extraction tools are available in the current environment. Prioritize in this order:

## Tier 1 - MCP Tools (if available)

```python
# Perplexity MCP (자체 크롤러로 네이버 블로그 포함 대부분의 차단 사이트 접근 가능)
mcp__perplexity__perplexity_search(query="...")
mcp__perplexity__perplexity_research(query="...")

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

## Tier 2.5 - Fallback Strategy (접근 불가 시 우회)

WebSearch/WebFetch 실패 시 아래 순서로 우회 시도. 네이버 블로그뿐 아니라 **모든 접근 불가 사이트**에 적용한다.

### 1. 모바일 URL 변환 + curl (네이버 블로그 등 UA 차단 우회)

도메인별 최적 방법을 먼저 확인하고, 해당하면 즉시 적용:

| 도메인 패턴 | 최적 방법 |
|-----------|---------|
| `blog.naver.com` | 모바일 URL + iPhone UA |
| `*.tistory.com` | WebFetch (정상 작동) 또는 RSS |
| `brunch.co.kr` | WebFetch (정상 작동) |
| `linkedin.com` | WebSearch → WebFetch (정상 작동) |
| `*.naver.com` (기타) | Playwright MCP (JS 렌더링 필요) |
| 페이월 사이트 | Google 캐시 → Wayback → 대체 소스 |

```bash
# 네이버 블로그: blog.naver.com/{ID}/{NO} → m.blog.naver.com 모바일 변환
curl -sL \
  -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1" \
  -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" \
  -H "Accept-Language: ko-KR,ko;q=0.9" \
  -H "Referer: https://m.naver.com/" \
  "https://m.blog.naver.com/PostView.naver?blogId={ID}&logNo={NO}"
# se-text-paragraph 클래스에서 본문 추출

# 일반 사이트: 모바일 UA로 봇 감지 우회
curl -sL \
  -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15" \
  "{URL}"
```

### 2. RSS 피드 확인 (블로그/뉴스 최신 포스트 일괄 수집)

API 키 불필요. 블로그/뉴스 사이트에 특히 유효:

```bash
# 네이버 블로그 RSS — 최신 50개 포스트 제목+링크+본문 300자
curl -sL "https://rss.blog.naver.com/{BLOG_ID}.xml"

# 티스토리 RSS
curl -sL "https://{blogname}.tistory.com/rss"

# 워드프레스 RSS
curl -sL "https://{domain}/feed"
```

### 3. OGP 메타태그 추출 (Googlebot UA — 최소 제목+요약 확보)

본문 전체는 못 가져오지만 요약+제목은 확보 가능:

```bash
curl -sL \
  -H "User-Agent: Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" \
  "{URL}" \
  | grep -E '<meta property="og:|<meta name="description'
```

### 4. Google 캐시 / Wayback Machine (캐시된 버전 시도)

```bash
# Google 캐시
curl -sL "https://webcache.googleusercontent.com/search?q=cache:{URL}"

# Wayback Machine
curl -sL "https://web.archive.org/web/{URL}"
```

단, iframe 기반 사이트(네이버)는 캐시도 실패할 수 있음.

### 5. curl_cffi (Cloudflare 등 TLS 핑거프린트 차단 우회)

```python
# pip install curl_cffi 필요
from curl_cffi import requests
response = requests.get("{URL}", impersonate="chrome124")
print(response.text)
```

### 6. Playwright MCP (JS 렌더링 필요한 SPA — 최후 수단)

```bash
# 설치: claude mcp add playwright npx @playwright/mcp@latest
# CC에서 자연어로 브라우저 제어 가능
```

JS 렌더링이 필수인 SPA 사이트(네이버 부동산 등)에만 사용. 가장 느리지만 거의 모든 사이트 접근 가능.

### Fallback 실행 규칙

1. **우회 성공 시**: 소스 신뢰도에 `via_fallback` 태그 추가, 어떤 방법으로 성공했는지 기록
2. **모든 우회 실패 시**: 실패 URL + 각 우회 방법별 시도 결과를 `sources/failed_urls.txt`에 기록
3. **대체 소스 재검색**: 동일 주제의 다른 소스를 WebSearch로 재검색 (원본 URL의 제목/키워드 추출 → 새 검색어)

---

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
