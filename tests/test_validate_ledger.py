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
    "type": "official_docs",
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
    "type": "independent_benchmark",
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
        "counter_search": {
            "query": "refute test claim 2026",
            "urls": [],
            "summary": "no refutation found",
        },
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


# --- 데이터 흐름 락 하드닝 (v2.9.0) ---


def test_process_violation_revokes_verified_allowlist(tmp_path):
    """exit 1이면 verified_claims.json을 만들지 않고 gate_failed.json을 남긴다."""
    s = make_session(
        tmp_path,
        [SRC_A, SRC_B],
        [base_claim(), base_claim(claim_id="clm_002", counter_search="")],
    )
    r = run_gate(s)
    assert r.returncode == 1, r.stderr
    assert not (s / "outputs" / "verified_claims.json").exists()
    marker = load_outputs(s, "gate_failed.json")
    assert marker["kind"] == "process_violation"
    assert any("clm_002" in x for x in marker["reasons"])


def test_stale_verified_is_deleted_on_later_failure(tmp_path):
    """통과했던 세션이 이후 실패하면 이전 allowlist가 남지 않는다 (스테일 우회 차단)."""
    s = make_session(tmp_path, [SRC_A, SRC_B], [base_claim()])
    assert run_gate(s).returncode == 0
    assert (s / "outputs" / "verified_claims.json").exists()

    (s / "artifacts" / "claim_ledger.jsonl").write_text(
        json.dumps(base_claim(counter_search=""), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    r = run_gate(s)
    assert r.returncode == 1, r.stderr
    assert not (s / "outputs" / "verified_claims.json").exists()
    assert load_outputs(s, "gate_failed.json")["verified_claims_removed"] is True


def test_hard_error_revokes_verified_and_marks_state(tmp_path):
    s = make_session(tmp_path, [SRC_A, SRC_B], [base_claim()])
    assert run_gate(s).returncode == 0

    (s / "artifacts" / "claim_ledger.jsonl").write_text(
        json.dumps(base_claim(source_ids=["src_999"]), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    r = run_gate(s)
    assert r.returncode == 2, r.stderr
    assert not (s / "outputs" / "verified_claims.json").exists()
    assert load_outputs(s, "gate_failed.json")["kind"] == "hard_error"
    state = json.loads((s / "state.json").read_text(encoding="utf-8"))
    assert state["verification"]["passed"] is False
    assert state["verification"]["blocked"] == "hard_error"


def test_pass_clears_stale_gate_marker(tmp_path):
    """실패 후 고쳐서 통과하면 gate_failed.json이 사라진다."""
    s = make_session(tmp_path, [SRC_A, SRC_B], [base_claim(counter_search="")])
    assert run_gate(s).returncode == 1
    assert (s / "outputs" / "gate_failed.json").exists()

    (s / "artifacts" / "claim_ledger.jsonl").write_text(
        json.dumps(base_claim(), ensure_ascii=False) + "\n", encoding="utf-8"
    )
    r = run_gate(s)
    assert r.returncode == 0, r.stderr
    assert not (s / "outputs" / "gate_failed.json").exists()
    assert len(load_outputs(s, "verified_claims.json")) == 1


def test_unresolved_ratio_warning_recorded(tmp_path):
    """미확정 비율이 임계치를 넘으면 통과하되 경고 + state 기록."""
    claims = [
        base_claim(),
        base_claim(claim_id="clm_002", source_ids=["src_001"]),
        base_claim(claim_id="clm_003", source_ids=["src_001"]),
    ]
    s = make_session(tmp_path, [SRC_A, SRC_B], claims)
    r = run_gate(s)
    assert r.returncode == 0, r.stderr
    assert "[WARN]" in r.stderr
    state = json.loads((s / "state.json").read_text(encoding="utf-8"))
    assert state["verification"]["unresolved_ratio"] > 0.5
    assert state["verification"]["passed"] is True


# --- 자기신고 → 증적 승격 + 조직 독립성 (v2.9.0 Step 1·2) ---


def test_legacy_string_counter_is_violation(tmp_path):
    """자유 문자열 counter_search는 감사 불가 → high-risk에서 절차 위반."""
    s = make_session(tmp_path, [SRC_A, SRC_B], [base_claim(counter_search="반증 없음")])
    r = run_gate(s)
    assert r.returncode == 1, r.stderr
    assert "자유 문자열" in r.stderr


def test_counter_url_must_be_registered(tmp_path):
    """counter_search.urls의 URL이 sources.jsonl에 없으면 하드 에러."""
    c = base_claim(
        counter_search={
            "query": "refute q",
            "urls": ["https://unregistered.example.net/refute"],
            "summary": "반박 시도 확인",
        }
    )
    s = make_session(tmp_path, [SRC_A, SRC_B], [c])
    r = run_gate(s)
    assert r.returncode == 2, r.stderr
    assert "counter_search.urls에 미등록 URL" in r.stderr


def test_counter_url_registered_passes(tmp_path):
    """등록된 URL을 가리키는 counter_search는 통과 (슬래시 차이 정규화 포함)."""
    c = base_claim(
        counter_search={
            "query": "refute q",
            "urls": ["https://b.example.org/y/"],
            "summary": "반박 없음",
        }
    )
    s = make_session(tmp_path, [SRC_A, SRC_B], [c])
    r = run_gate(s)
    assert r.returncode == 0, r.stderr
    assert len(load_outputs(s, "verified_claims.json")) == 1


def test_same_org_subdomains_count_once(tmp_path):
    """peps.python.org + docs.python.org 류 — 같은 조직 서브도메인 2개는 독립 1개."""
    a = dict(SRC_A, id="src_001", url="https://peps.python.org/p", domain="peps.python.org")
    b = dict(SRC_B, id="src_002", url="https://docs.python.org/d", domain="docs.python.org",
             type="official_docs")
    s = make_session(tmp_path, [a, b], [base_claim()])
    r = run_gate(s)
    assert r.returncode == 0, r.stderr
    unresolved = load_outputs(s, "unresolved_claims.json")
    assert len(unresolved) == 1
    assert "독립 출처(조직) 1개" in unresolved[0]["status_reason"]


def test_hosting_domain_subdomains_are_distinct_orgs(tmp_path):
    """github.io 같은 호스팅 도메인은 서브도메인이 곧 별개 주체 — 독립 2개."""
    a = dict(SRC_A, id="src_001", url="https://alpha.github.io/x", domain="alpha.github.io")
    b = dict(SRC_B, id="src_002", url="https://beta.github.io/y", domain="beta.github.io")
    s = make_session(tmp_path, [a, b], [base_claim()])
    r = run_gate(s)
    assert r.returncode == 0, r.stderr
    assert len(load_outputs(s, "verified_claims.json")) == 1


def test_explicit_org_field_overrides_inference(tmp_path):
    """소스의 org 필드가 같으면 도메인이 달라도 독립 1개."""
    a = dict(SRC_A, org="acme")
    b = dict(SRC_B, org="acme")
    s = make_session(tmp_path, [a, b], [base_claim()])
    r = run_gate(s)
    assert r.returncode == 0, r.stderr
    assert "독립 출처(조직) 1개" in load_outputs(s, "unresolved_claims.json")[0]["status_reason"]


def test_primary_source_is_derived_not_self_reported(tmp_path):
    """주장이 primary_source=true라 우겨도 1차 type 소스가 없으면 미도달."""
    a = dict(SRC_A, type="news")
    b = dict(SRC_B, type="blog")
    s = make_session(tmp_path, [a, b], [base_claim(primary_source=True)])
    r = run_gate(s)
    assert r.returncode == 0, r.stderr
    rec = load_outputs(s, "unresolved_claims.json")[0]
    assert "1차 소스 미도달" in rec["status_reason"]
    assert rec["primary_source"] is False  # 출력 레코드도 파생값으로 덮어씀


def test_surface_diversity_required_for_high_risk(tmp_path):
    """조직 2개라도 표면(type)이 1종이면 high-risk는 미충족."""
    a = dict(SRC_A, type="official_docs")
    b = dict(SRC_B, type="official_docs")
    s = make_session(tmp_path, [a, b], [base_claim()])
    r = run_gate(s)
    assert r.returncode == 0, r.stderr
    assert "표면(type) 1종" in load_outputs(s, "unresolved_claims.json")[0]["status_reason"]


def test_normal_risk_unaffected_by_high_risk_rules(tmp_path):
    """normal 주장은 counter 구조체·1차소스·표면 다양성 규칙 미적용."""
    a = dict(SRC_A, type="news")
    b = dict(SRC_B, type="news")
    c = base_claim(risk="normal", counter_search="", primary_source=False)
    s = make_session(tmp_path, [a, b], [c])
    r = run_gate(s)
    assert r.returncode == 0, r.stderr
    assert len(load_outputs(s, "verified_claims.json")) == 1
