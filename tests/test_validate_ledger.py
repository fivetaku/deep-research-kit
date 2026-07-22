"""validate_ledger.py 게이트의 결정론적 exit code 계약 테스트.

실행: 레포 루트에서 `python3 -m pytest tests/ -q`
서브프로세스로 스크립트를 그대로 호출해 CLI 계약(exit 0/1/2)을 검증한다.
"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "insane-research-main"
    / "scripts"
    / "validate_ledger.py"
)

SRC_A = {
    "id": "src_001",
    "url": "https://a.example.com/x",
    "title": "A",
    "domain": "a.example.com",
    "quality_rating": "B",
    "observed_at": "2026-07-22T15:00:00Z",
    "valid_at": "2026-06-01",
    "access": {"layer": "insane-search", "verdict": "strong_ok"},
}
SRC_B = {
    "id": "src_002",
    "url": "https://b.example.org/y",
    "title": "B",
    "domain": "b.example.org",
    "quality_rating": "B",
    "observed_at": "2026-07-22T15:01:00Z",
    "valid_at": "2026-06-02",
}


def make_session(tmp_path, sources, claims):
    (tmp_path / "artifacts").mkdir()
    (tmp_path / "sources").mkdir()
    (tmp_path / "outputs").mkdir()
    (tmp_path / "sources" / "sources.jsonl").write_text(
        "\n".join(json.dumps(s, ensure_ascii=False) for s in sources) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "artifacts" / "claim_ledger.jsonl").write_text(
        "\n".join(json.dumps(c, ensure_ascii=False) for c in claims) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "state.json").write_text(
        json.dumps({"session_id": "fixture", "progress": {}}), encoding="utf-8"
    )
    return tmp_path


def run_gate(session):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--session", str(session)],
        capture_output=True,
        text=True,
    )


def load_outputs(session, name):
    return json.loads((session / "outputs" / name).read_text(encoding="utf-8"))


def base_claim(**over):
    claim = {
        "claim_id": "clm_001",
        "text": "test claim",
        "risk": "high",
        "claim_type": "numeric",
        "source_ids": ["src_001", "src_002"],
        "counter_search": "no refutation found",
        "counter_refuted": False,
        "conflicting": False,
        "primary_source": True,
        "valid_at": "2026-06-01",
    }
    claim.update(over)
    return claim


# --- 기존 동작 회귀 ---


def test_verified_pass_exit0(tmp_path):
    s = make_session(tmp_path, [SRC_A, SRC_B], [base_claim()])
    r = run_gate(s)
    assert r.returncode == 0, r.stderr
    assert len(load_outputs(s, "verified_claims.json")) == 1


def test_high_risk_missing_counter_exit1(tmp_path):
    s = make_session(tmp_path, [SRC_A, SRC_B], [base_claim(counter_search="")])
    r = run_gate(s)
    assert r.returncode == 1, r.stderr


def test_unknown_source_id_exit2(tmp_path):
    s = make_session(tmp_path, [SRC_A], [base_claim(source_ids=["src_999"])])
    r = run_gate(s)
    assert r.returncode == 2, r.stderr


def test_domain_grade_conflict_exit2(tmp_path):
    src_dup = dict(SRC_B, id="src_003", domain="a.example.com", quality_rating="C")
    s = make_session(tmp_path, [SRC_A, src_dup], [base_claim()])
    r = run_gate(s)
    assert r.returncode == 2, r.stderr


def test_single_domain_unresolved_exit0(tmp_path):
    s = make_session(tmp_path, [SRC_A], [base_claim(source_ids=["src_001"])])
    r = run_gate(s)
    assert r.returncode == 0, r.stderr
    assert len(load_outputs(s, "unresolved_claims.json")) == 1
    assert len(load_outputs(s, "verified_claims.json")) == 0


# --- executable 실행 검증 (M3 신규) ---


def exec_claim(**over):
    claim = base_claim(
        claim_type="executable",
        source_ids=["src_001"],
        counter_search="",
    )
    claim.update(over)
    return claim


def test_executable_missing_proof_exit1(tmp_path):
    s = make_session(tmp_path, [SRC_A], [exec_claim()])
    r = run_gate(s)
    assert r.returncode == 1, r.stderr
    assert "execution_proof" in r.stderr


def test_executable_confirmed_verified_single_source(tmp_path):
    proof = {
        "script": "python3 repro.py",
        "output": "OK 42",
        "env": "macOS/py3.12",
        "verdict": "confirmed",
    }
    s = make_session(tmp_path, [SRC_A], [exec_claim(execution_proof=proof)])
    r = run_gate(s)
    assert r.returncode == 0, r.stderr
    verified = load_outputs(s, "verified_claims.json")
    assert len(verified) == 1
    assert verified[0]["status_reason"].startswith("실행 검증 통과")


def test_executable_refuted_goes_to_refuted_exit0(tmp_path):
    proof = {"script": "python3 repro.py", "output": "FAIL", "verdict": "refuted"}
    s = make_session(tmp_path, [SRC_A], [exec_claim(execution_proof=proof)])
    r = run_gate(s)
    assert r.returncode == 0, r.stderr
    assert len(load_outputs(s, "refuted_claims.json")) == 1
    assert len(load_outputs(s, "verified_claims.json")) == 0


def test_executable_partial_unresolved_exit0(tmp_path):
    proof = {"script": "python3 repro.py", "output": "…", "verdict": "partial"}
    s = make_session(tmp_path, [SRC_A], [exec_claim(execution_proof=proof)])
    r = run_gate(s)
    assert r.returncode == 0, r.stderr
    assert len(load_outputs(s, "unresolved_claims.json")) == 1


def test_executable_bogus_verdict_exit1(tmp_path):
    proof = {"script": "x", "output": "y", "verdict": "maybe"}
    s = make_session(tmp_path, [SRC_A], [exec_claim(execution_proof=proof)])
    r = run_gate(s)
    assert r.returncode == 1, r.stderr
