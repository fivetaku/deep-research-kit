"""eval_report.py 채점기의 leak/annex/citation 계약 테스트."""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "insane-research-main"
    / "scripts"
    / "eval_report.py"
)

UNRESOLVED_TEXT = "특정 벤더 설문에서 응답자 91%가 전환 의향을 밝혔다"


def make_session(tmp_path, report_md):
    (tmp_path / "outputs").mkdir()
    (tmp_path / "sources").mkdir()
    (tmp_path / "sources" / "sources.jsonl").write_text(
        json.dumps({"id": "src_001", "url": "https://a.example.com", "domain": "a.example.com"})
        + "\n",
        encoding="utf-8",
    )
    verified = [{"claim_id": "clm_v1", "text": "확정 사실은 버전 9.9.9다", "status": "verified"}]
    unresolved = [{"claim_id": "clm_u1", "text": UNRESOLVED_TEXT, "status": "unresolved"}]
    (tmp_path / "outputs" / "verified_claims.json").write_text(
        json.dumps(verified, ensure_ascii=False), encoding="utf-8"
    )
    (tmp_path / "outputs" / "unresolved_claims.json").write_text(
        json.dumps(unresolved, ensure_ascii=False), encoding="utf-8"
    )
    (tmp_path / "outputs" / "refuted_claims.json").write_text("[]", encoding="utf-8")
    (tmp_path / "outputs" / "report.md").write_text(report_md, encoding="utf-8")
    return tmp_path


def run_eval(session):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--session", str(session)],
        capture_output=True,
        text=True,
    )


BASE = "# 보고서\n\n확정 사실은 버전 9.9.9다 (src_001).\n\n"


def test_annex_quote_is_not_leak(tmp_path):
    """미확정 주장을 Unresolved annex 안에 그대로 나열해도 leak이 아니다."""
    md = BASE + "## Unresolved\n\n1. " + UNRESOLVED_TEXT + "\n"
    r = run_eval(make_session(tmp_path, md))
    assert r.returncode == 0, r.stderr
    assert "PASS" in r.stderr


def test_korean_annex_heading_also_excluded(tmp_path):
    md = BASE + "## 미확정 목록\n\n- " + UNRESOLVED_TEXT + "\n"
    r = run_eval(make_session(tmp_path, md))
    assert r.returncode == 0, r.stderr


def test_body_leak_still_fails(tmp_path):
    """annex 밖 본문에 미확정 주장이 단정형으로 등장하면 여전히 FAIL."""
    md = BASE + "## 결론\n\n" + UNRESOLVED_TEXT + ".\n\n## Unresolved\n\n(없음)\n"
    r = run_eval(make_session(tmp_path, md))
    assert r.returncode == 1, r.stderr
    assert "clm_u1" in r.stderr


def test_annex_ends_at_next_heading(tmp_path):
    """annex 다음 동급 헤딩부터는 다시 스캔 대상 — 그 뒤에 등장하면 FAIL."""
    md = (
        BASE
        + "## Unresolved\n\n(항목 없음)\n\n## 부록 해설\n\n"
        + UNRESOLVED_TEXT
        + "\n"
    )
    r = run_eval(make_session(tmp_path, md))
    assert r.returncode == 1, r.stderr


def test_dangling_citation_fails(tmp_path):
    md = BASE + "미등록 인용 (src_999).\n"
    r = run_eval(make_session(tmp_path, md))
    assert r.returncode == 1, r.stderr
