# Changelog

## [2.8.1] - 2026-07-23

### Changed — 엔진 위임 비동기 기본화

- insane-search 위임을 **background-first 패턴**으로 전환: 백그라운드 시작 → ~15초 빠른 수거(대부분 경로는 여기서 인라인과 동일) → 미완료 시 다음 조사 병행 → **반환 전 전량 수거 게이트(불가침)**, URL당 90초 초과 시 실패 기록 후 대체 소스 전환. 어려운 WAF 격자(최악 ~65초, 벤치에서 17회 시도 실측)가 에이전트 전체를 세워두는 문제 해소. 같은 도메인에서 긴 격자를 겪은 뒤에는 폴링 없이 바로 병행. `access` 메타에 `async` 표시.
- 조건 판정형(R7식 발동 조건) 대신 기본 패턴으로 설계한 이유: 에이전트가 실행 중 verdict를 관찰할 수 없어 조건형은 실전에서 발동되지 않기 때문.

## [2.8.0] - 2026-07-23

### Added — Workflow 팬아웃 모드 (공식 문서 + 실측 프로브 근거)

- **Phase 3 실행 모드 선택**: 세션에 Workflow 도구가 있으면 **팬아웃 모드**(폭 5-6, `references/workflow_fanout.md`), 없으면 기존 배치 모드(2-3, Rate-Limit Guard) 폴백. 실측: 6폭 버스트 6/6 무사고(3.8s), 리서치형 5폭 5/5 무사고(16s).
- **AGENT_RETURN_SCHEMA 강제 반환 + 결정론 취합기** `scripts/merge_agent_returns.py`: 에이전트 JSON 반환 배열 → sources.jsonl(URL dedup·전역 id)/claim_ledger.jsonl(URL→id 매핑)/expansion_log.md/query_log.md(교차 에이전트 쿼리 중복 표시) 자동 생성 — 벤치 실측 병목(수작업 병합 ~7분) 제거. 취합 산출물이 validate_ledger 게이트에 무수정으로 물리는 것까지 테스트(총 19 pytest).
- **검색 예산 회계**: Claude Code 세션당 WebSearch 200회 캡(전 서브에이전트 합산, 초과 시 조용한 no-op — v2.1.212+) 대응. 축당 예산 배분, search_count 합산·80% 경고, "빈 검색 연속 = 캡 의심" 진단 규칙.
- **WebFetch 손실성 명시**: "부재 판정은 WebFetch로 하지 않는다" (공식 lossy-by-design 근거).

## [2.7.0] - 2026-07-22

### Added — ULW 흡수 (insane 강점 유지 + ulw-research 메커니즘 채용)

근거: `RESEARCH/lazycodex_ulw_vs_insane_20260722_140015/outputs/` 비교 분석 2편.

- **접근 3단 에스컬레이션 (P1-0)**: Phase 3 접근을 WebFetch → **insane-search 엔진 위임**(설치 시, `python3 -m engine --json --trace` 계약 + `⛔ NOT EXHAUSTED`/untried_routes 준수 + R8 untrusted 취급) → 내장 폴백 체인으로 명문화. tool_strategy.md에 엔진 탐지·호출 계약 섹션 신설, 접근 SSOT를 insane-search 플러그인으로 선언(드리프트 방지). sources.jsonl에 `access` 메타(layer/verdict/profile_used/extraction_source/phase) 추가.
- **EXPAND 리드 확장 루프 (P1-1)**: 모든 리서치 에이전트 응답 꼬리에 `## EXPAND`(LEAD/WHY/ANGLE | DEAD END | none) 필수. `artifacts/expansion_log.md` 전수 dedup(기각 리드 포함) + 명시적 수렴 규칙(미확인 리드 0 / 2연속 무신규 배치 / 깊이 4 도달 시 사용자 질의). 확장 배치는 기존 Rate-Limit Guard(2-3 동시) 내에서만.
- **executable 실행 검증 (P1-2)**: `claim_type: "executable"` + `execution_proof`(script/output/env/verdict) 스키마 추가. `validate_ledger.py`가 executable 주장에 실행 증적을 강제 — 누락 시 exit 1, confirmed는 독립 교차검증 대체, refuted/partial은 annex행. `tests/test_validate_ledger.py` 신규(10 케이스: 기존 회귀 5 + executable 5).
- **스폰 메시지 표준 3요소 (P1-3)**: agent_prompts.md에 예산 해제문·완료 정의·EXPAND 꼬리 필수화 — 서브에이전트의 "찾으면 정지" 브레이크를 명시적으로 풀지 않으면 얕은 답이 돌아오는 문제 대응.
- **검색 크래프트 (P1-4)**: tool_strategy.md에 연산자 변주 표(site:/filetype:/intitle:/inurl:/exact/-term/OR/before:/after:), 에이전트당 최소 8-10 상이 쿼리, 고수익 조합, 언어 정책(주제 1차 언어 우선 스윕).
- **시간 유효성 분리 (P2)**: sources·ledger에 `observed_at`(수집 시각)/`valid_at`(내용 유효 시점) 필드 — 릴리즈 노트/과거 기사/현재 상태 주장 혼동 방지.
- **리포트 시각화 기본화 (P2)**: full_report_section.md에 Mermaid 다이어그램 슬롯("정량은 차트, 구조·인과는 Mermaid"), website_template.html에 mermaid@11.16.0(SRI 핀) + 다이어그램 블록.

### Added — 실전 벤치마크(2026-07-22, vs ulw-research) 후속 보강
- **eval_report.py annex 예외**: Unresolved/Refuted annex 섹션은 leak 스캔에서 제외(헤딩 기반 섹션 스트립) — 계약이 요구하는 annex 나열이 leak으로 오탐되던 모순 해소. `tests/test_eval_report.py` 신규(5 케이스: annex 인용 무해·한국어 헤딩·본문 누출 FAIL 유지·annex 경계·dangling 회귀).
- **다중 표면 삼각측량**: 도메인 독립 ≠ 내용 대조 — 조직 구성/버전/법률 주장은 이질 표면(공식 페이지 vs 저장소 파일 vs 기계판독 API) 대조를 요구(SKILL.md Phase 4 + tool_strategy.md). 벤치에서 도메인 2개 통과 주장의 표면 충돌(TSC 소속)이 실측된 데서 도출.
- **표준 분모 소스**: 채택률·점유율 주장은 벤더 설문 대신 중립 분모(SO Developer Survey·DB-Engines·repology) 우선 — 크래프트 고수익 조합에 추가.

### Fixed
- tool_strategy.md 스테일 접근 경로 정정: Reddit 비인증 `.json`+모바일 UA 안내 폐기(WAF 403 실측) → `.rss`+curl_cffi로 교체, Google 캐시(2024-07 종료) 제거 → Wayback/archive.today로 대체.

### Infra (마켓플레이스 레포)
- `tools/validate_skill_contracts.py` — 불가침 계약 문구 18종 grep-assert CI 게이트, validate-commands 워크플로우에 연결.

## [2.6.0] - 2026-06-22

### Added
- **`scripts/eval_report.py` — 결정론적 평가 채점기**(측정 도구, LLM judge 없음). 리서치 세션 산출물을 받아 검증 게이트의 실제 효과를 4지표로 계측:
  - `leak_rate`(unresolved/refuted 주장이 본문에 샜는가 — verified-only 게이트 효과의 직접 지표), `citation_resolution_rate`(깨진 인용), `orphan_source_rate`(미인용 소스), `verified_coverage_rate`(allowlist가 실제 소비됐는가).
  - leak/coverage 판별은 content char 6-gram + verified 맥락 제외로 버전번호 등 공유 토큰 오탐 방지. verdict FAIL(leak 또는 dangling citation 존재) 시 exit 1.
  - good/bad 픽스처로 판별력 검증(GOOD=PASS leak0, BAD=FAIL leak2+dangling+orphan).
- SKILL.md Phase 7에 마감 자기검증(`eval_report.py`) 단계 추가, Scripts 표에 authoritative 등록.

### Why
"개선이 진짜 효과 있나"를 측정할 수단이 없었음(GPT 리뷰도 평가 harness 부재 지적). 이제 검증 게이트 효과를 숫자로 확인하고, 이후 개선마다 게이트 on/off A/B·회귀 추적 가능.

## 2.5.1 — 2026-06-21

- The GitHub-star prompt is shown in the user's current language; on a fresh session with no language signal yet, it falls back to the language detected from your recent Claude sessions (else English).
- GitHub star is now **opt-in** — on first run the command asks once via AskUserQuestion (`네, ⭐ 눌러주기` / `아니요`) instead of auto-starring. The star logic moved into `setup.sh` and records the choice (`~/.gptaku-setup/<plugin>.star.json`) so it never re-asks. `setup.sh` no longer stars anything automatically.

## [2.5.0] - 2026-06-21

### Added
- **`scripts/validate_ledger.py` — 결정론적 검증 게이트** (control plane이 아닌 단일 체커).
  - claim ledger(`artifacts/claim_ledger.jsonl`) + `sources.jsonl`을 읽어 주장 status를 **코드로 계산**(독립 도메인 ≥2, counter_search 존재, 1차소스, B등급 이상).
  - `outputs/verified_claims.json` 생산 + `state.json`에 sha256 `verification.signature` 기록.
  - 종료코드: 0=통과 / 1=프로세스 위반(high-risk counter_search 누락) / 2=하드 에러(스키마·미등록 source id·**A-E 등급 모순**).

### Changed
- **SKILL.md 검증을 "권고"에서 "코드 게이트"로 전환** (agent-council B 노선 + GPT-5.5 Pro 리뷰 반영):
  - Phase 4: claim ledger를 `artifacts/claim_ledger.jsonl`(JSONL)로 명문화, `status`는 체커가 계산(직접 작성 금지).
  - Phase 5: **verified-only 합성 게이트** — 핵심 주장은 `outputs/verified_claims.json`만 근거(데이터 흐름 락).
  - Phase 6: `validate_ledger.py` 실행을 명령과 함께 **하드 게이트**로 규정(exit≠0 시 Phase 7 진입 금지).
  - A-E 등급표를 `quality_rubric.md` SSOT에 정렬(Gartner/McKinsey research=B 등 파일 간 모순 해소).
  - 스코핑 우선순위를 단일 규칙으로 통합("무조건 즉시 질문" 충돌 제거).
  - Scripts 표에서 `orchestrator.py`/`pipelines.py`를 helper(정적 자산)로 강등, `validate_ledger.py`를 authoritative로.
- `tool_strategy.md` 병렬 에이전트 예시를 기본 **foreground 배치**로 수정(경고와 모순되던 `run_in_background=True` 복붙 예시 제거).

### Why
GPT-5.5 Pro 코드리뷰: SKILL.md 검증 계약과 Python 코드가 미연결 → 검증이 LLM 자율에 의존(권고). classify_claim_status가 counter_search 존재조차 검사 안 함, 합성이 raw findings를 그대로 수용. agent-council(agy/Claude) 합의 = "오케스트레이션은 프롬프트, 검증은 코드"로 분리하고 단일 결정론 체커를 스킬이 반드시 호출하게.

## [2.2.2] - 2026-05-04

### Changed
- SKILL.md "Research Type별 권장 골격" → **"Research Type 기반 골격 동적 생성"**
  - 5 type 표를 "메뉴"가 아닌 "패턴 학습용 예시"로 명시
  - 적용 절차에 "**사용자 주제에 맞춰 5 섹션 명을 동적 생성**" 단계 추가
  - 섹션 명을 그대로 카피하지 말고 사용자 주제에 맞춰 변환하라 명시
  - "새 type 사례를 본 표에 추가하지 말 것" 가드 추가

### Why
v2.2.1의 type별 매핑 표가 약한 fossil 위험 (섹션 명 하드코딩).
사용자 지적: 카탈로그를 메뉴로 쓰면 새 fossil이 됨 → 예시 + 동적 생성으로 명시.

## [2.2.1] - 2026-05-04

### Added
- SKILL.md "Research Type별 권장 골격" 섹션 — Exploratory/Comparative/Predictive/Analytical/Generic 5 type 매핑 (advanced opt-in)

### Preserved (모든 결정 contract 그대로 유지)
- 7-Phase 강제 + 기본 5섹션 보고서 골격 (resume protocol)
- A-E source quality 등급 + minimum 2 sources
- citation 5 elements (Author/Date/Title/URL/Page)
- Hallucination Prevention 4 strategies
- state.json / sources.jsonl schema
- Date-aware query generation (CRITICAL)

→ ADDITIVE only. 기본 동작은 그대로, type별 골격은 사용자 명시 confirm 시에만 사용.

## [2.2.0] - 2026-03-16

### Added
- Tier 2.5 fallback strategy — 차단된 사이트에 대한 대체 접근 전략 추가

## [2.1.0] - 2026-03-10

### Fixed
- allowed-tools에서 AskUserQuestion 제거 — auto-approve로 UI가 렌더링되지 않던 버그 해결
- SKILL.md에 EXECUTE 키워드 + markdown preview 적용

### Changed
- .gitattributes 추가 — CRLF/LF 정규화

## [2.0.0] - 2026-02-28

### Changed
- 멀티에이전트 소스 검증 파이프라인 도입 (7단계)
- 구조화된 리포트 생성 기능 강화
- plugin.json 메타데이터 보강 (homepage, repository, license 추가)

## [1.1.0] - 2026-02-25

### Changed
- CCPS v2.0 플러그인 표준으로 전체 구조 리팩토링

## [1.0.1] - 2026-02-24

### Fixed
- README 영문 통일, 로컬 저장 이점 설명 보강

## [1.0.0] - 2026-02-23

### Added
- 최초 릴리스
- AI 기반 딥 리서치 스킬
- 로컬 저장소에 리서치 결과 자동 저장
