# Deep Research Kit

> Claude Code용 AI 기반 딥 리서치 스킬 - 상태 관리, 소스 검증, 구조화된 출력을 갖춘 종합 리서치 시스템

모호한 연구 질문을 Claude의 에이전트 기능을 활용하여 포괄적이고 잘 인용된 보고서로 변환합니다.

## 데모

```
User: /deep-research "2024년 AI 코드 어시스턴트가 개발자 생산성에 미치는 영향"

Claude:
1. 명확화 질문 (범위, 대상, 형식)
2. 하위 주제로 연구 계획 수립
3. 병렬 에이전트로 검색 및 소스 수집
4. 여러 소스 간 교차 검증
5. 인용이 포함된 종합 보고서 생성

결과물: RESEARCH/AI_Code_Assistants_20260129_143000/outputs/
├── 00_executive_summary.md
├── 01_full_report/
└── sources/bibliography.md
```

## 설치

### npx로 설치 (권장)

```bash
npx github:fivetaku/deep-research-kit
```

`.claude/skills/deep-research/`에 스킬 파일을 복사합니다.

**옵션:**
```bash
# 현재 프로젝트에 설치 (.claude/ 존재 시 기본값)
npx github:fivetaku/deep-research-kit --project

# 전역 설치 (~/.claude/skills/)
npx github:fivetaku/deep-research-kit --global

# 특정 CLI 지정
npx github:fivetaku/deep-research-kit --target claude   # Claude Code
npx github:fivetaku/deep-research-kit --target codex    # Codex CLI
npx github:fivetaku/deep-research-kit --target gemini   # Gemini CLI
npx github:fivetaku/deep-research-kit --target both     # Claude + Codex
npx github:fivetaku/deep-research-kit --target all      # 모든 CLI
```

### 수동 설치

```bash
# 저장소 클론
git clone https://github.com/fivetaku/deep-research-kit.git

# 프로젝트에 복사
cp -r deep-research-kit/plugins/deep-research/skills/deep-research YOUR_PROJECT/.claude/skills/

# 또는 홈 디렉토리에 복사 (전역)
cp -r deep-research-kit/plugins/deep-research/skills/deep-research ~/.claude/skills/
```

### 삭제

```bash
rm -rf ~/.claude/skills/deep-research
# 또는
rm -rf .claude/skills/deep-research
```

## 사용법

### 새 리서치 시작

```
/deep-research "연구 주제"
```

### 구조화된 쿼리 사용 (고급)

```
/deep-research {
  "task": {"title": "AI 헬스케어 연구", "objective": "...", "type": "analytical"},
  "context": {"audience": "executive", ...},
  "questions": {"primary": "...", "secondary": [...]},
  "constraints": {"timeframe": {...}, "sources": {...}},
  "output": {"format": "comprehensive_report", ...}
}
```

### 이전 세션 재개

```
/research-status          # 모든 세션 목록
/research-resume <id>     # 마지막 체크포인트에서 계속
```

### 대화형 쿼리 빌더

```
/research-query           # 가이드된 쿼리 구성
```

## 출력 위치

모든 리서치 결과물은 다음 위치에 저장됩니다:

```
RESEARCH/{topic}_{timestamp}/
├── state.json              # 세션 상태 (재개 가능)
├── README.md               # 탐색 가이드
│
├── outputs/                # <<< 최종 결과물
│   ├── 00_executive_summary.md
│   ├── 01_full_report/
│   │   ├── 01_introduction.md
│   │   ├── 02_methodology.md
│   │   ├── 03_findings.md
│   │   └── 04_conclusions.md
│   └── 02_appendices/
│
├── sources/
│   ├── sources.jsonl       # 원본 소스 데이터
│   ├── bibliography.md     # 형식화된 인용
│   └── quality_report.md   # 소스 품질 분석
│
└── website/                # 선택적 HTML 시각화
    └── index.html
```

## 7단계 파이프라인

| 단계 | 이름 | 설명 |
|------|------|------|
| 1 | **질문 범위 지정** | 연구 질문 명확화, 요구사항 정의 |
| 2 | **검색 계획** | 하위 주제로 분해, 검색 쿼리 생성 |
| 3 | **반복 쿼리** | 병렬 검색 실행, 소스 수집 |
| 4 | **소스 삼각검증** | 교차 참조, 2개 이상 소스로 검증 |
| 5 | **지식 합성** | 발견 사항 병합, 인용 포함 초안 작성 |
| 6 | **품질 보증** | 환각 확인, 모든 인용 검증 |
| 7 | **출력 및 패키징** | 최종 결과물 생성 |

## 소스 품질 등급

| 등급 | 설명 | 예시 |
|------|------|------|
| **A** | 동료 심사, 체계적 리뷰 | Nature, Lancet, IEEE |
| **B** | 공식 문서, 가이드라인 | FDA, W3C, 공식 문서 |
| **C** | 전문가 의견, 보고서 | Gartner, 컨퍼런스 |
| **D** | 예비 연구, 프리프린트 | arXiv, 백서 |
| **E** | 일화적, 추측적 | 블로그, 소셜 미디어 |

## 프로젝트 구조

```
deep-research-kit/
├── bin/
│   └── install.js              # npx 인스톨러
├── plugins/
│   └── deep-research/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── SKILL.md
│       └── skills/
│           └── deep-research/
│               ├── SKILL.md         # 스킬 정의
│               ├── scripts/
│               │   ├── orchestrator.py
│               │   └── pipelines.py
│               ├── references/
│               │   ├── quality_rubric.md
│               │   ├── citation_rules.md
│               │   └── phase_contracts.md
│               └── assets/templates/
│                   ├── executive_summary.md
│                   ├── bibliography.md
│                   └── website_template.html
├── package.json
├── README.md
└── README.ko.md
```

## 쿼리 생성기

모호한 아이디어를 구조화된 연구 쿼리로 변환:

1. 아무 LLM(ChatGPT, Claude, Gemini) 열기
2. 시스템 프롬프트를 `prompts/query_generator_system.md`로 설정
3. 연구 주제 설명
4. 명확화 질문에 답변
5. 구조화된 JSON 쿼리 받기
6. `/deep-research [JSON]`으로 사용

## 다른 딥 리서치 도구와의 차이점

| 기능 | 이 키트 | OpenAI Deep Research | Google Gemini |
|------|---------|---------------------|---------------|
| **상태 관리** | ✅ 재개 가능한 세션 | ❌ | ❌ |
| **소스 검증** | ✅ A-E 품질 등급 | ⚠️ 기본 | ⚠️ 기본 |
| **출력 구조** | ✅ 모듈식 폴더 | 단일 문서 | 단일 문서 |
| **커스터마이징** | ✅ JSON 스키마 | 제한적 | 제한적 |
| **로컬 제어** | ✅ 내 파일 | 클라우드만 | 클라우드만 |
| **비용** | Claude 구독 | $200/월 | Gemini Advanced |

## 최상의 결과를 위한 팁

1. **구체적으로** - "2024년 헬스케어 방사선 AI" > "헬스케어 AI"
2. **대상 정의** - 기술팀 vs 경영진에 따라 깊이와 톤이 달라짐
3. **시간 범위 설정** - "2023년 이후"로 오래된 소스 방지
4. **소스 유형 지정** - 학술 전용 vs 산업 보고서 포함
5. **JSON 쿼리 사용** - 재현 가능하고 정밀한 연구를 위해

## 문제 해결

### 리서치가 너무 오래 걸림
- 범위 축소 (하위 주제 줄이기)
- 소스 요구사항 감소
- `min_quality: "C"` 대신 "B" 사용

### 소스 누락
- 검색어 확장
- 더 많은 소스 유형 포함
- 시간 범위 확장

### 재개가 안됨
- `RESEARCH/*/state.json` 존재 확인
- session_id 철자 확인

## 요구사항

- **Claude Code** 에이전트 기능
- **Python 3.8+** (오케스트레이터 스크립트용)
- **Node.js 16+** (npx 설치용)

## 기여

기여를 환영합니다! 다음을 자유롭게 추가해주세요:
- 새 출력 템플릿
- 검색 전략 개선
- 검증 방법 향상
- 언어 지원 추가

## 라이선스

MIT 라이선스 - 자세한 내용은 [LICENSE](LICENSE)를 참조하세요.

## 크레딧

- OpenAI와 Google 딥 리서치 방법론에서 영감을 받음
- [Claude Code](https://claude.ai/code)용으로 제작
