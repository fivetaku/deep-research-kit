# Changelog

## [2.3.0] - 2026-03-18

### Changed
- DRY 대규모 정리: 소스 품질 등급(4중 중복 → quality_rubric.md 정본), QA 체크리스트, 명확화 질문 등 pipelines.py 중복 상수 제거
- query_generator.md 삭제 (deep-research-query/SKILL.md가 정본)
- pipelines.py 날짜 하드코딩 → 동적 _date_range_recent/_broad() 함수로 교체
- Task 도구명 → Agent 도구명 통일 (SKILL.md, agent_prompts.md, tool_strategy.md)
- Agent 프롬프트 내 MCP 도구명 하드코딩 → 일반화
- orchestrator.py __main__ → CLI 인자 수용
- Phase 이름 한영 매핑 표 추가

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
