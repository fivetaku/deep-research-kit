#!/usr/bin/env python3
"""
verify_report.py — 보고서 본문 ↔ claim ledger 대조 게이트 (Phase 7 직전 필수).

validate_ledger.py가 "어떤 주장이 검증됐는가"를 결정한다면, 이 스크립트는
**"검증된 주장만 본문에 단정형으로 쓰였는가"** 를 확인한다. 둘 사이를 잇는 코드가
없으면 게이트를 통과시킨 뒤 본문에 미검증 문장을 쓰는 걸 잡을 방법이 없다.

검사 항목:
  1) 게이트 상태 — outputs/gate_failed.json 이 있으면 애초에 합성하면 안 되는 상태 (exit 2)
  2) 미검증 인용 — unresolved/refuted claim_id가 **본문**(annex 밖)에 인용되면 위반 (exit 1)
  3) 유령 인용 — ledger에 없는 claim_id 인용 (exit 1)
  4) 인용 커버리지 — verified 주장 중 본문에 인용된 비율 (기본 경고, --min-coverage로 강제)

annex 판정: 마크다운 제목이 미확정/Unresolved/반증/Refuted/부록/Annex/Appendix 를 포함하는
섹션은 미검증 주장을 나열해도 되는 구역으로 본다(그 목적의 섹션이므로).

입력:
  <session>/outputs/{verified,unresolved,refuted}_claims.json  (validate_ledger 산출)
  <session>/outputs/*.md                                       (보고서 — --report로 지정 가능)

종료 코드:
  0  통과
  1  본문 계약 위반 (미검증 인용·유령 인용·커버리지 미달)
  2  하드 에러 (게이트 실패 상태·검증 산출물 없음·보고서 없음)
"""

import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime, timezone

CLAIM_ID_RE = re.compile(r"\bclm[_-][A-Za-z0-9][A-Za-z0-9_.-]*", re.IGNORECASE)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
ANNEX_WORDS = (
    "미확정",
    "확인 필요",
    "unresolved",
    "반증",
    "refuted",
    "부록",
    "annex",
    "appendix",
)


def _load_json(path, default=None):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return default


def _is_annex_heading(title):
    low = title.lower()
    return any(w in low for w in ANNEX_WORDS)


def split_sections(text):
    """
    마크다운을 (heading, is_annex, body) 섹션 목록으로 자른다.
    제목 앞의 본문은 heading=None(=본문 취급)으로 둔다.
    하위 제목은 상위 annex 구역을 상속한다.
    """
    sections = []
    cur_title, cur_annex, cur_level, buf = None, False, 0, []
    for line in text.splitlines():
        m = HEADING_RE.match(line)
        if not m:
            buf.append(line)
            continue
        sections.append((cur_title, cur_annex, "\n".join(buf)))
        level, title = len(m.group(1)), m.group(2).strip()
        if _is_annex_heading(title):
            cur_annex, cur_level = True, level
        elif cur_annex and level <= cur_level:
            # annex 구역과 같거나 상위 레벨의 새 제목 → 구역 종료
            cur_annex, cur_level = False, 0
        cur_title, buf = title, []
    sections.append((cur_title, cur_annex, "\n".join(buf)))
    return sections


def _cited_ids(text):
    return {m.group(0).lower().replace("-", "_") for m in CLAIM_ID_RE.finditer(text)}


def scan_report(path):
    """보고서 1개에서 (본문 인용 집합, annex 인용 집합) 반환."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    body_ids, annex_ids = set(), set()
    for title, is_annex, body in split_sections(text):
        chunk = f"{title or ''}\n{body}"
        ids = _cited_ids(chunk)
        (annex_ids if is_annex else body_ids).update(ids)
    return body_ids, annex_ids


def verify(session, report_paths, min_coverage, state_path):
    out_dir = os.path.join(session, "outputs")
    hard, violations, warnings = [], [], []
    if state_path and os.path.exists(state_path):
        # An interrupted or failed recheck must not leave an earlier pass usable.
        _stamp_state(state_path, False, None, None)

    gate_failed_path = os.path.join(out_dir, "gate_failed.json")
    if os.path.exists(gate_failed_path):
        hard.append(
            "게이트 실패 상태 (gate_failed.json 존재) — 합성/보고서 작성 자체가 금지된 상태다. "
            f"validate_ledger.py를 통과시킨 뒤 다시 실행."
        )

    verified = _load_json(os.path.join(out_dir, "verified_claims.json"))
    if verified is None:
        hard.append(
            "outputs/verified_claims.json 없음 — validate_ledger.py 미실행 또는 게이트 실패."
        )
    unresolved = _load_json(os.path.join(out_dir, "unresolved_claims.json"), []) or []
    refuted = _load_json(os.path.join(out_dir, "refuted_claims.json"), []) or []

    if not report_paths:
        hard.append(f"보고서 파일 없음: {out_dir}/*.md")
    for path in report_paths:
        if not os.path.isfile(path):
            hard.append(f"보고서 파일 없음: {path}")

    if hard:
        if state_path and os.path.exists(state_path):
            _stamp_state(state_path, False, None, None, hard_errors=hard)
        _report(hard, [], [], None, None)
        return 2

    def ids_of(records):
        return {
            str(r.get("claim_id", "")).lower().replace("-", "_")
            for r in records
            if r.get("claim_id")
        }

    verified_ids = ids_of(verified)
    unresolved_ids = ids_of(unresolved)
    refuted_ids = ids_of(refuted)
    known_ids = verified_ids | unresolved_ids | refuted_ids

    body_all, annex_all = set(), set()
    for path in report_paths:
        body, annex = scan_report(path)
        rel = os.path.relpath(path, session)
        for cid in sorted(body & unresolved_ids):
            violations.append(f"{rel}: 미확정 주장 {cid} 를 본문에 인용 (annex로 이동 필요)")
        for cid in sorted(body & refuted_ids):
            violations.append(f"{rel}: 반증된 주장 {cid} 를 본문에 인용 (Refuted 섹션 전용)")
        for cid in sorted((body | annex) - known_ids):
            violations.append(f"{rel}: 유령 인용 {cid} — ledger에 없는 claim_id")
        body_all |= body
        annex_all |= annex

    cited_verified = body_all & verified_ids
    coverage = (len(cited_verified) / len(verified_ids)) if verified_ids else 1.0

    if verified_ids and not cited_verified:
        violations.append(
            f"본문에 verified 주장 인용이 0건 — 검증 결과가 보고서에 연결되지 않았다 "
            f"(verified {len(verified_ids)}건). 핵심 주장 문장에 (clm_XXX)를 표기할 것."
        )
    elif coverage < min_coverage:
        violations.append(
            f"인용 커버리지 {coverage:.0%} < 요구치 {min_coverage:.0%} "
            f"({len(cited_verified)}/{len(verified_ids)} verified 주장만 본문에 인용됨)"
        )
    elif coverage < 0.5:
        warnings.append(
            f"인용 커버리지 {coverage:.0%} — 검증한 주장의 절반 이상이 본문에 쓰이지 않았다."
        )

    if state_path and os.path.exists(state_path):
        _stamp_state(state_path, not violations, coverage, len(violations))

    _report(hard, violations, warnings, coverage, (len(cited_verified), len(verified_ids)))
    return 1 if violations else 0


def _stamp_state(state_path, passed, coverage, violation_count, *, hard_errors=()):
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
    except (OSError, json.JSONDecodeError):
        return
    state["report_verification"] = {
        "passed": passed,
        "citation_coverage": round(coverage, 4) if coverage is not None else None,
        "violation_count": violation_count,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "checker": "verify_report.py",
    }
    if hard_errors:
        state["report_verification"]["hard_errors"] = list(hard_errors)
    tmp = state_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, state_path)


def _report(hard, violations, warnings, coverage, cited):
    out = sys.stderr
    print("=== verify_report 결과 ===", file=out)
    if hard:
        print(f"\n[HARD ERROR] {len(hard)}건 (exit 2):", file=out)
        for e in hard:
            print(f"  - {e}", file=out)
        return
    if cited:
        print(f"  본문 인용 verified {cited[0]}/{cited[1]}  커버리지={coverage:.0%}", file=out)
    for w in warnings:
        print(f"  [WARN] {w}", file=out)
    if violations:
        print(f"\n[FAIL] 본문 계약 위반 {len(violations)}건 (exit 1):", file=out)
        for v in violations:
            print(f"  - {v}", file=out)
    else:
        print("  → 통과. 본문은 verified 주장만 단정형으로 인용한다.", file=out)


def main():
    p = argparse.ArgumentParser(description="보고서 본문 ↔ claim ledger 대조 게이트")
    p.add_argument("--session", required=True, help="리서치 세션 폴더 (RESEARCH/{topic}_{ts})")
    p.add_argument(
        "--report",
        action="append",
        help="검사할 보고서 경로 (반복 지정 가능. 기본: <session>/outputs/*.md)",
    )
    p.add_argument(
        "--min-coverage",
        type=float,
        default=0.0,
        help="verified 주장 중 본문 인용 비율 최소치 (기본 0.0 = 강제 안 함)",
    )
    p.add_argument("--state", help="state.json 경로 (기본: <session>/state.json)")
    args = p.parse_args()

    reports = args.report or sorted(glob.glob(os.path.join(args.session, "outputs", "*.md")))
    state = args.state or os.path.join(args.session, "state.json")
    sys.exit(verify(args.session, reports, args.min_coverage, state))


if __name__ == "__main__":
    main()
