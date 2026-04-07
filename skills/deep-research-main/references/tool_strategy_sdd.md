# tool_strategy.md 재설계 SDD

> 작성일: 2026-04-07
> 대상: `plugins/deep-research/skills/deep-research-main/references/tool_strategy.md`

---

## 1. 현재 문제점 요약

현행 `tool_strategy.md`는 MCP 도구(Perplexity, Firecrawl, Google Search MCP, Exa)를 **Tier 1 — 최우선 도구**로 배치하고, WebSearch/WebFetch를 Tier 2로 격하시켜 놓았다. 이 구조는 MCP가 설치된 환경에서는 효과적이지만, **MCP가 없는 환경(대다수의 사용자 환경)에서는 Tier 1 전체가 사용 불가**가 되어 리서치 에이전트가 즉시 Tier 2로 떨어지고, 플랫폼별 접근 전략(X/Twitter, Reddit, YouTube 등)이 전혀 안내되지 않아 리서치 품질이 급락한다.

또한 `pipelines.py`의 에이전트 프롬프트에 `mcp_google_search`, `mcp_websearch`, `mcp_webfetch`, `mcp_context7`, `mcp_grep_app` 등 MCP 도구명이 하드코딩되어 있어, MCP 미설치 환경에서 에이전트가 존재하지 않는 도구를 호출 시도하고 실패하는 문제가 있다.

현행 Tier 넘버링(1/2/2.5/3)은 "숫자가 낮을수록 우선"이라는 암시를 주어, 에이전트가 MCP 없이는 열등한 도구를 쓰고 있다는 잘못된 인식을 형성한다.

---

## 2. 설계 원칙

### 원칙 1: 항상 가용한 도구가 기본이다

WebSearch, WebFetch, Bash(curl)는 모든 Claude Code 환경에서 항상 사용 가능하다. 이것이 리서치의 기본 체계이며, MCP는 이를 **강화하는 부스터**일 뿐이다.

### 원칙 2: 플랫폼별 최적 접근법을 명시한다

X/Twitter, Reddit, YouTube 등 주요 플랫폼은 각각 고유한 접근 방법이 있다. "WebSearch로 검색하라"는 범용 지침 대신, 플랫폼별로 **실제 테스트를 통해 검증된 명령어**를 제공한다.

### 원칙 3: Tier 넘버링을 제거하고 역할 기반 섹션으로 구분한다

"Tier 1/2/3" 대신 "기본 도구 / 플랫폼별 전략 / Fallback / MCP 부스터 / 특수 도구"로 섹션을 나눈다. 우선순위가 아니라 **역할**로 구분한다.

### 원칙 4: 응답 검증 규칙을 추가한다

curl로 받은 응답이 실제 콘텐츠인지, 로그인 페이지/CAPTCHA/에러 페이지인지 판별하는 명확한 기준을 제공한다.

---

## 3. 새 구조 — 섹션별 설계

### 3.1 기본 도구 (항상 가용)

MCP 설치 여부와 무관하게 모든 Claude Code 환경에서 사용 가능한 도구들. **리서치의 주력 도구**다.

#### WebSearch — 검색

```python
# 범용 웹 검색 (항상 사용 가능)
WebSearch(query="AI code assistants 2026 latest trends")

# 특정 사이트 한정 검색
WebSearch(query="site:x.com openclaw dreaming feature")
WebSearch(query="site:reddit.com ClaudeAI third-party harness")

# 학술 검색
WebSearch(query="transformer architecture survey 2025 arxiv")
```

**역할**: 검색 결과(제목, snippet, URL) 획득. 모든 리서치의 시작점.

#### WebFetch — 콘텐츠 추출

```python
# URL에서 콘텐츠 추출
WebFetch(url="https://example.com/article", prompt="Extract key findings and data")
```

**역할**: 검색에서 발견한 URL의 본문 추출. 대부분의 일반 웹페이지에서 동작.

**제한**: x.com(402), reddit.com(차단), 네이버 블로그(차단) 등 일부 사이트에서 실패 → 플랫폼별 전략 또는 Fallback으로 전환.

#### Bash(curl) — 직접 HTTP 요청

```bash
# 범용 웹페이지 읽기 (Jina Reader)
curl -s "https://r.jina.ai/https://example.com/article"

# RSS 피드 수집
python3 -c "
import feedparser
for e in feedparser.parse('FEED_URL').entries[:5]:
    print(f'{e.title} — {e.link}')
"
```

**역할**: WebFetch가 실패하는 사이트 우회, API 직접 호출, 플랫폼별 전략 실행.

#### 사용 순서

1. **WebSearch**로 검색하여 관련 URL 확보
2. **WebFetch**로 URL 본문 추출 시도
3. WebFetch 실패 시 → **Bash(curl)**로 우회 (Jina Reader, 플랫폼별 API, Fallback 순)

---

### 3.2 플랫폼별 접근 전략

각 플랫폼의 최적 접근법. 모두 **API 키 불필요, 인증 불필요**로 동작한다.

#### X/Twitter

WebFetch는 402로 차단됨. 아래 방법을 사용.

**검색 (트윗 발견)**

```python
# WebSearch로 트윗 URL 발견
WebSearch(query="site:x.com {검색어}")
```

**타임라인 조회 — Syndication API (최적)**

인증 불필요. 특정 핸들의 최근 ~20개 트윗 + engagement 수치(likes, RTs) 제공.

```bash
curl -sL "https://syndication.twitter.com/srv/timeline-profile/screen-name/{handle}"
```

데이터 파싱:

```bash
curl -sL "https://syndication.twitter.com/srv/timeline-profile/screen-name/{handle}" | \
python3 -c "
import sys, json, re, html
content = sys.stdin.read()
match = re.search(r'__NEXT_DATA__.*?>(.*?)</script>', content)
if match:
    data = json.loads(match.group(1))
    for e in data['props']['pageProps']['timeline']['entries']:
        if e['type'] == 'tweet':
            t = e['content']['tweet']
            print(f\"@{t['user']['screen_name']} ({t.get('created_at','?')})\")
            print(f\"  {html.unescape(t.get('full_text',''))[:300]}\")
            print(f\"  Likes: {t.get('favorite_count',0)} | RTs: {t.get('retweet_count',0)}\")
            print('---')
"
```

가져올 수 있는 데이터: `full_text`, `screen_name`, `name`, `favorite_count`, `retweet_count`, `created_at`, `id_str`, `media_url_https`

제한: 최근 ~20개만, 비공개 계정 불가, 검색 불가(타임라인만)

**개별 트윗 조회 — oEmbed API**

특정 트윗 URL을 알 때 전문 가져오기.

```bash
curl -sL "https://publish.twitter.com/oembed?url=https://x.com/{user}/status/{tweet_id}"
```

응답(JSON): `author_name`, `author_url`, `html`(트윗 전문 포함)

**조합 패턴 (검색 → 상세)**

```
1단계: WebSearch(query="site:x.com {키워드}") → 트윗 URL 획득
2단계: curl oEmbed API → 트윗 전문 획득
```

**실패하는 방법**: WebFetch(402), Nitter(종료됨), Wayback(SPA 미렌더링), RSS(X는 지원 중단)

---

#### Reddit

WebFetch는 www/old 모두 차단됨. 아래 방법을 사용.

**JSON API — URL 뒤에 `.json`만 붙이면 된다 (최적)**

인증 불필요. **단, Mobile User-Agent 헤더 필수** (없으면 403/429).

```bash
# 서브레딧 핫 포스트
curl -sL \
  -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15" \
  "https://www.reddit.com/r/{subreddit}/hot.json?limit=10"

# 서브레딧 검색
curl -sL \
  -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15" \
  "https://www.reddit.com/r/{subreddit}/search.json?q={query}&restrict_sr=1"

# 개별 포스트 + 댓글
curl -sL \
  -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15" \
  "https://www.reddit.com/r/{subreddit}/comments/{post_id}/{slug}/.json"

# 유저 프로필
curl -sL \
  -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15" \
  "https://www.reddit.com/user/{username}/.json"
```

엔드포인트 패턴:
- `/r/{subreddit}/.json` — 포스트 목록
- `/r/{subreddit}/hot.json?limit=N` — 인기 포스트
- `/r/{subreddit}/new.json?limit=N` — 최신 포스트
- `/r/{subreddit}/top.json?t=week&limit=N` — 상위 포스트 (t: hour/day/week/month/year/all)
- `/r/{subreddit}/search.json?q={query}&restrict_sr=1` — 서브레딧 내 검색
- `/r/{subreddit}/comments/{post_id}/{slug}/.json` — 포스트 + 댓글

포스트 데이터: `title`, `author`, `score`, `selftext`(본문 마크다운), `url`, `num_comments`, `created_utc`, `link_flair_text`

댓글 데이터: 응답의 `[1]` 배열에 댓글 트리 — `author`, `body`, `score`, `replies`(재귀적)

파싱 스크립트:

```bash
curl -sL \
  -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15" \
  "https://www.reddit.com/r/{subreddit}/hot.json?limit=10" | \
python3 -c "
import sys, json
data = json.load(sys.stdin)
for post in data['data']['children']:
    d = post['data']
    print(f\"[{d.get('score',0)}] {d['title']}\")
    print(f\"  by u/{d['author']} | {d.get('num_comments',0)} comments\")
    body = d.get('selftext','')
    if body:
        print(f\"  {body[:200]}\")
    print('---')
"
```

**실패하는 방법**: WebFetch(차단), RSS(403, 2023년 이후 비인증 차단)

---

#### YouTube

**자막 추출 — yt-dlp (최적)**

```bash
# 자막 다운로드 (영상 다운로드 없이)
yt-dlp --write-sub --write-auto-sub --sub-lang "zh-Hans,zh,en,ko" --skip-download -o "/tmp/%(id)s" "URL"

# 자막 파일 읽기
cat /tmp/VIDEO_ID.*.vtt
```

**영상 메타데이터**

```bash
yt-dlp --dump-json "URL"
```

**영상 검색**

```bash
yt-dlp --dump-json "ytsearch5:{검색어}"
```

**댓글 추출**

```bash
yt-dlp --write-comments --skip-download --write-info-json \
  --extractor-args "youtube:max_comments=20" \
  -o "/tmp/%(id)s" "URL"
# 댓글은 .info.json의 comments 필드에 저장
```

주의: 자동 생성 자막은 행간 중복 가능 → 후처리 필요. 댓글은 웹 스크래핑 기반이라 일부 누락 가능.

---

#### GitHub

```bash
# 저장소 검색
gh search repos "{query}" --sort stars --limit 10

# 코드 검색
gh search code "{query}" --language python --limit 10

# 이슈 검색
gh search issues "{query}" --repo {owner}/{repo} --limit 10

# PR 검색
gh search prs "{query}" --repo {owner}/{repo} --limit 10

# 저장소 README 읽기
gh api repos/{owner}/{repo}/readme --jq '.content' | base64 -d
```

---

#### 범용 웹 — Jina Reader

WebFetch 실패 시 대체. 대부분의 일반 웹페이지를 마크다운으로 변환.

```bash
# Jina Reader — URL 앞에 r.jina.ai/ 붙이기
curl -s "https://r.jina.ai/https://example.com/article"
```

제한: 미신 공중호(mp.weixin.qq.com) 등 CAPTCHA 보호 사이트는 실패.

---

#### RSS 피드

API 키 불필요. 블로그/뉴스 사이트의 최신 포스트 일괄 수집에 유용.

```bash
# 네이버 블로그 RSS — 최신 50개 포스트 제목+링크+본문 300자
curl -sL "https://rss.blog.naver.com/{BLOG_ID}.xml"

# 티스토리 RSS
curl -sL "https://{blogname}.tistory.com/rss"

# 워드프레스 RSS
curl -sL "https://{domain}/feed"

# Python feedparser로 파싱
python3 -c "
import feedparser
for e in feedparser.parse('FEED_URL').entries[:10]:
    print(f'{e.title} — {e.link}')
    print(f'  {e.get(\"summary\",\"\")[:200]}')
    print('---')
"
```

---

### 3.3 접근 불가 시 우회 전략 (Fallback)

WebSearch/WebFetch/플랫폼별 전략 모두 실패했을 때 아래 순서로 우회 시도. **모든 접근 불가 사이트**에 적용한다.

#### 1. 모바일 URL 변환 + curl (UA 차단 우회)

도메인별 최적 방법을 먼저 확인:

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

#### 2. RSS 피드 확인

```bash
curl -sL "https://rss.blog.naver.com/{BLOG_ID}.xml"
curl -sL "https://{blogname}.tistory.com/rss"
curl -sL "https://{domain}/feed"
```

#### 3. OGP 메타태그 추출 (최소 제목+요약 확보)

```bash
curl -sL \
  -H "User-Agent: Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" \
  "{URL}" \
  | grep -E '<meta property="og:|<meta name="description'
```

#### 4. Google 캐시 / Wayback Machine

```bash
# Google 캐시
curl -sL "https://webcache.googleusercontent.com/search?q=cache:{URL}"

# Wayback Machine
curl -sL "https://web.archive.org/web/{URL}"
```

단, iframe 기반 사이트(네이버)는 캐시도 실패할 수 있음.

#### 5. curl_cffi (TLS 핑거프린트 차단 우회)

```python
# pip install curl_cffi 필요
from curl_cffi import requests
response = requests.get("{URL}", impersonate="chrome124")
print(response.text)
```

#### 6. Playwright MCP (JS 렌더링 필요한 SPA — 최후 수단)

MCP 부스터 섹션 참조. JS 렌더링이 필수인 SPA에만 사용.

#### 응답 검증 규칙 (Fallback 성공 판정 기준)

curl 등으로 받은 응답이 **실제 콘텐츠인지** 아래 기준으로 판별한다:

| 판정 | 조건 | 조치 |
|------|------|------|
| **성공** | 본문 텍스트 1,000자 이상 + 주제 관련 키워드 포함 | 소스로 사용 |
| **부분 성공** | OG 메타태그나 제목+요약만 추출됨 (본문 없음) | 보조 소스로 사용, `partial_content` 태그 |
| **실패 — 로그인 페이지** | `login`, `sign in`, `로그인`, `password` 키워드가 본문 상단에 집중 | 다음 Fallback 시도 |
| **실패 — CAPTCHA** | `captcha`, `verify`, `robot`, `보안 인증` 키워드 또는 본문 200자 미만 | 다음 Fallback 시도 |
| **실패 — 에러 페이지** | HTTP 4xx/5xx 응답 또는 `404`, `not found`, `access denied` 키워드 | 다음 Fallback 시도 |
| **실패 — 빈 SPA** | HTML은 있으나 `<noscript>`, `<div id="root"></div>` 외 실질 콘텐츠 없음 | Playwright MCP 또는 포기 |

#### Fallback 실행 규칙

1. **우회 성공 시**: 소스 신뢰도에 `via_fallback` 태그 추가, 어떤 방법으로 성공했는지 기록
2. **모든 우회 실패 시**: 실패 URL + 각 우회 방법별 시도 결과를 `sources/failed_urls.txt`에 기록
3. **대체 소스 재검색**: 동일 주제의 다른 소스를 WebSearch로 재검색 (원본 URL의 제목/키워드 추출 → 새 검색어)

---

### 3.4 MCP 부스터 (선택적)

환경에 설치되어 있으면 **우선 활용**한다. 없어도 기본 도구로 충분한 리서치가 가능하다.

> **사용 조건**: 해당 MCP 도구가 현재 환경에서 호출 가능할 때만 사용. 없으면 무시하고 기본 도구를 사용한다.

#### Perplexity MCP

자체 크롤러로 네이버 블로그 포함 대부분의 차단 사이트 접근 가능. 검색 + 콘텐츠 추출을 한번에 수행.

```python
mcp__perplexity__perplexity_search(query="...")
mcp__perplexity__perplexity_research(query="...")   # 심층 리서치
```

**대체 방법(MCP 없을 때)**: WebSearch + WebFetch 조합, 또는 Jina Reader

#### Firecrawl MCP

웹 크롤링 + 콘텐츠 추출 특화. 검색과 스크래핑 모두 가능.

```python
firecrawl_search(query="...", limit=10)
firecrawl_scrape(url="...")
```

**대체 방법**: WebSearch + Jina Reader(`curl r.jina.ai/URL`)

#### Exa MCP

심층 검색. 의미 기반 검색으로 일반 키워드 검색보다 정확도 높음.

```python
mcp_websearch_web_search_exa(query="...", type="deep", numResults=10)
```

**대체 방법**: WebSearch(여러 쿼리 변형으로 보완)

#### Google Search MCP

```python
mcp_google_search(query="...", thinking=True)
```

**대체 방법**: WebSearch (동일 엔진 기반)

#### Playwright MCP

JS 렌더링이 필수인 SPA 사이트(네이버 부동산, X/Twitter 프로필 등) 접근. 가장 느리지만 거의 모든 사이트 접근 가능.

```bash
# 설치: claude mcp add playwright npx @playwright/mcp@latest
# CC에서 자연어로 브라우저 제어 가능
```

**대체 방법**: 해당 플랫폼의 API(Syndication API, JSON API 등) 사용

---

### 3.5 특수 도구 (선택적)

특정 도메인에 특화된 도구들. MCP 설치 여부에 따라 사용.

#### GitHub MCP / gh CLI

```python
# MCP 사용 가능 시
mcp_grep_app_searchGitHub(query="...", language=["Python", "TypeScript"])

# 항상 사용 가능한 대체: gh CLI
# gh search repos "query" --sort stars --limit 10
# gh search code "query" --language python --limit 10
```

#### Context7 (라이브러리 문서)

```python
# MCP 사용 가능 시
mcp_context7_resolve_library_id(libraryName="react", query="hooks")
mcp_context7_query_docs(libraryId="/facebook/react", query="useEffect")
```

**대체 방법**: WebSearch로 공식 문서 검색 + WebFetch/Jina Reader로 추출

---

## 4. SKILL.md 수정 사항

### 현재 (변경 전)

`SKILL.md`의 Tool Usage 섹션 (L253-L259):

```
## Tool Usage

Use whichever search and extraction tools are available. Prioritize: MCP tools (Firecrawl, Google Search, Exa) > Built-in tools (WebSearch, WebFetch) > Specialized tools (GitHub search, library docs).
```

### 변경 후

```
## Tool Usage

기본 도구(WebSearch, WebFetch, Bash/curl)로 리서치를 수행한다. 플랫폼별 최적 접근법은 tool_strategy.md를 참조한다.
환경에 MCP 도구(Perplexity, Firecrawl, Exa 등)가 설치되어 있으면 우선 활용하되, 없어도 기본 도구만으로 충분한 리서치가 가능하다.
```

### Error Handling 섹션 (L474-L478)

현재:

```
### Network Failures
- Retry up to 3 times with backoff
- If still failing → Execute Tier 2.5 Fallback Strategy (`tool_strategy.md` 참조)
  - 모바일 UA curl → RSS 피드 → OGP 메타태그 → Google 캐시/Wayback → curl_cffi → Playwright MCP
```

변경:

```
### Network Failures
- Retry up to 3 times with backoff
- If still failing → tool_strategy.md의 "접근 불가 시 우회 전략 (Fallback)" 참조
  - 모바일 UA curl → RSS 피드 → OGP 메타태그 → Google 캐시/Wayback → curl_cffi → Playwright MCP
- 응답 검증 규칙으로 성공/실패 판정 (로그인 페이지, CAPTCHA, 빈 SPA 감지)
```

### Phase 3 섹션 (L200-L202)

현재:

```
- WebFetch 실패 시 → `tool_strategy.md` Tier 2.5 Fallback 순서대로 시도
```

변경:

```
- WebFetch 실패 시 → `tool_strategy.md`의 플랫폼별 접근 전략 또는 Fallback 순서대로 시도
```

---

## 5. 에이전트 프롬프트 영향

### 5.1 pipelines.py — MCP 하드코딩 제거

#### `explore_current_state` 프롬프트 (L113-L116)

현재:

```python
Use these tools:
1. mcp_google_search for recent news and reports
2. mcp_websearch for deep web search
3. mcp_webfetch to extract content from URLs
```

변경:

```python
Use these tools:
1. WebSearch for discovering recent news, reports, and source URLs
2. WebFetch to extract content from discovered URLs
3. Bash(curl) for platforms where WebFetch fails (see tool_strategy.md for platform-specific commands)
If MCP tools (Perplexity, Firecrawl, Exa, Google Search) are available, use them for enhanced coverage.
```

#### `librarian_docs` 프롬프트 (L160-L162)

현재:

```python
Use:
1. mcp_context7 for library documentation
2. mcp_grep_app for GitHub code examples
3. mcp_google_search for official specs
```

변경:

```python
Use:
1. WebSearch for official documentation and specs
2. gh CLI (gh search code, gh search repos) for code examples
3. WebFetch or Jina Reader (curl r.jina.ai/URL) to extract documentation content
If MCP tools (Context7, grep.app) are available, use them for enhanced search.
```

#### `default_factory` (L22)

현재:

```python
tools: List[str] = field(default_factory=lambda: ["google_search"])
```

변경:

```python
tools: List[str] = field(default_factory=lambda: ["WebSearch", "WebFetch", "Bash"])
```

### 5.2 agent_prompts.md

현재 이 파일에는 MCP 도구명이 직접 기재되어 있지 않다 (범용 프롬프트 템플릿 사용). **변경 불필요**.

다만, Agent Deployment Pattern 섹션에 다음 참조 문구를 추가하면 좋다:

```markdown
> 에이전트에게 플랫폼별 접근 전략이 필요한 경우, tool_strategy.md의 해당 섹션을 프롬프트에 포함시킨다.
```

---

## 6. 삭제/변경 대상

### 현행 tool_strategy.md에서 삭제하거나 이동할 내용

| 현행 섹션 | 조치 | 사유 |
|----------|------|------|
| `## Tier 1 - MCP Tools (if available)` | **삭제** → 3.4 MCP 부스터로 이동 | MCP를 최우선에서 선택적으로 강등 |
| `## Tier 2 - Built-in Tools` | **삭제** → 3.1 기본 도구로 재작성 | Tier 넘버링 제거, "기본"으로 승격 |
| `## Tier 2.5 - Fallback Strategy` | **유지** → 3.3 Fallback으로 이동 | 내용 유지, 응답 검증 규칙 추가 |
| `## Tier 3 - Specialized Tools` | **삭제** → 3.5 특수 도구로 이동 | Tier 넘버링 제거 |
| `## Background Agents for Parallel Research` | **유지** (위치 이동 없음) | 변경 불필요 |
| `## File Operations` | **유지** (위치 이동 없음) | 변경 불필요 |

### 새로 추가되는 내용

| 섹션 | 내용 | 근거 |
|------|------|------|
| 3.2 X/Twitter | Syndication API, oEmbed API, 조합 패턴 | X/Reddit 접근 테스트 리포트 검증 |
| 3.2 Reddit | JSON API (`.json` suffix + Mobile UA) | X/Reddit 접근 테스트 리포트 검증 |
| 3.2 YouTube | yt-dlp 자막/메타데이터/검색/댓글 | Agent Reach video.md 참조 |
| 3.2 GitHub | gh CLI 검색 명령어 | Agent Reach dev.md 참조 |
| 3.2 범용 웹 | Jina Reader (`curl r.jina.ai/URL`) | Agent Reach web.md 참조 |
| 3.2 RSS | feedparser, 네이버/티스토리/워드프레스 RSS | 기존 Tier 2.5 내용 승격 |
| 3.3 응답 검증 규칙 | 성공/실패 판정 테이블 | 신규 — Fallback 품질 보장 |

### 삭제되는 도구명 (기본 체계에서)

기본 체계 지침에서 아래 MCP 도구명은 모두 제거한다. MCP 부스터 섹션에서만 언급:

- `mcp__perplexity__perplexity_search`
- `mcp__perplexity__perplexity_research`
- `firecrawl_search` / `firecrawl_scrape`
- `mcp_google_search`
- `mcp_websearch_web_search_exa`
- `mcp_grep_app_searchGitHub`
- `mcp_context7_resolve_library_id` / `mcp_context7_query_docs`
