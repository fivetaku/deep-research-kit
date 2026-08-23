"""verify_report.py — 보고서 본문 ↔ ledger 대조 게이트의 exit code 계약 테스트."""

import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = (
    Path(__file__).resolve().parent.parent / "skills" / "insane-research-main" / "scripts"
)
SCRIPT = SCRIPTS / "verify_report.py"


def make_session(tmp_path, verified, unresolved, refuted, report, gate_failed=None):
    (tmp_path / "outputs").mkdir(parents=True, exist_ok=True)

    def rec(cid):
        return {"claim_id": cid, "text": f"주장 {cid}", "source_ids": ["src_001"]}

    for name, ids in (
        ("verified_claims.json", verified),
        ("unresolved_claims.json", unresolved),
        ("refuted_claims.json", refuted),
    ):
        (tmp_path / "outputs" / name).write_text(
            json.dumps([rec(c) for c in ids], ensure_ascii=False), encoding="utf-8"
        )
    (tmp_path / "outputs" / "01_full_report.md").write_text(report, encoding="utf-8")
    if gate_failed is not None:
        (tmp_path / "outputs" / "gate_failed.json").write_text(
            json.dumps(gate_failed), encoding="utf-8"
        )
    (tmp_path / "state.json").write_text(json.dumps({"session_id": "fx"}), encoding="utf-8")
    return tmp_path


def run(session, *extra):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--session", str(session), *extra],
        capture_output=True,
        text=True,
    )


GOOD_REPORT = """# 보고서

## 핵심 발견
시장은 성장했다 (clm_001).

## 미확정 (Unresolved)
- clm_002: 독립 출처 부족
"""


def test_clean_report_passes(tmp_path):
    s = make_session(tmp_path, ["clm_001"], ["clm_002"], [], GOOD_REPORT)
    r = run(s)
    assert r.returncode == 0, r.stderr
    state = json.loads((s / "state.json").read_text(encoding="utf-8"))
    assert state["report_verification"]["passed"] is True
    assert state["report_verification"]["citation_coverage"] == 1.0


def test_unresolved_cited_in_body_fails(tmp_path):
    report = "# 보고서\n\n## 핵심 발견\n확실히 30%다 (clm_001, clm_002).\n"
    s = make_session(tmp_path, ["clm_001"], ["clm_002"], [], report)
    r = run(s)
    assert r.returncode == 1
    assert "미확정 주장 clm_002" in r.stderr


def test_refuted_cited_in_body_fails(tmp_path):
    report = "# 보고서\n\n## 결론\n그렇다 (clm_001) 그리고 (clm_009).\n"
    s = make_session(tmp_path, ["clm_001"], [], ["clm_009"], report)
    r = run(s)
    assert r.returncode == 1
    assert "반증된 주장 clm_009" in r.stderr


def test_phantom_citation_fails(tmp_path):
    report = "# 보고서\n\n## 결론\n근거는 (clm_777)이다.\n"
    s = make_session(tmp_path, ["clm_001"], [], [], report)
    r = run(s)
    assert r.returncode == 1
    assert "유령 인용 clm_777" in r.stderr


def test_no_verified_citation_fails(tmp_path):
    report = "# 보고서\n\n## 결론\n서술만 있고 인용이 없다.\n"
    s = make_session(tmp_path, ["clm_001"], [], [], report)
    r = run(s)
    assert r.returncode == 1
    assert "인용이 0건" in r.stderr


def test_gate_failed_marker_is_hard_error(tmp_path):
    s = make_session(
        tmp_path,
        ["clm_001"],
        [],
        [],
        GOOD_REPORT,
        gate_failed={"kind": "process_violation", "reasons": ["clm_001: counter_search 누락"]},
    )
    r = run(s)
    assert r.returncode == 2
    assert "게이트 실패 상태" in r.stderr


def test_missing_verified_output_is_hard_error(tmp_path):
    s = make_session(tmp_path, ["clm_001"], [], [], GOOD_REPORT)
    (s / "outputs" / "verified_claims.json").unlink()
    r = run(s)
    assert r.returncode == 2
    assert "verified_claims.json 없음" in r.stderr


def test_min_coverage_enforced(tmp_path):
    report = "# 보고서\n\n## 결론\n하나만 인용한다 (clm_001).\n"
    s = make_session(tmp_path, ["clm_001", "clm_002", "clm_003"], [], [], report)
    assert run(s).returncode == 0  # 기본은 강제 안 함(경고만)
    r = run(s, "--min-coverage", "0.9")
    assert r.returncode == 1
    assert "커버리지" in r.stderr


def test_annex_subsection_scope_ends_at_next_top_heading(tmp_path):
    """annex 구역은 같은/상위 레벨 제목에서 끝난다 — 그 뒤 본문 인용은 다시 위반."""
    report = (
        "# 보고서\n\n## 미확정 (Unresolved)\n- clm_002\n\n"
        "### 세부\n- clm_002 재확인 필요\n\n"
        "## 결론\n확정이다 (clm_002).\n"
    )
    s = make_session(tmp_path, ["clm_001"], ["clm_002"], [], report)
    r = run(s)
    assert r.returncode == 1
    assert "미확정 주장 clm_002" in r.stderr
