"""strict_verification_handoff가 validate_ledger 실스키마 레코드를 소비하는지 검증."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..",
                                "skills", "insane-research-main", "scripts"))
from pipelines import strict_verification_handoff


LEDGER = [
    {"claim_id": "C1", "text": "위젯 처리량은 초당 500건이다",
     "source_ids": ["src_a"], "status": "verified", "status_reason": "실행 검증 통과"},
    {"claim_id": "C2", "text": "차기 버전에서 두 배가 된다",
     "source_ids": ["src_b"], "status": "unresolved", "status_reason": "단일 출처"},
    {"claim_id": "C3", "text": "규제 위반 벌금은 5억이다",
     "source_ids": ["src_c"], "status": "verified", "status_reason": "1차 출처",
     "high_risk": True},
    {"claim_id": "C4", "text": "status 없는 레코드", "source_ids": []},
]


def test_selects_unresolved_and_high_risk_only():
    out = strict_verification_handoff(LEDGER)
    ids = [p["claim_id"] for p in out]
    assert ids == ["C2", "C3", "C4"]  # verified(C1) 제외, status 부재(C4)는 미확정 취급


def test_payload_uses_real_schema_text():
    out = strict_verification_handoff(LEDGER)
    for p in out:
        assert p["claim"], "text 필드가 비어 있으면 스키마 드리프트"
        assert p["question"], "question이 비어 있으면 스키마 드리프트"
        assert p["workflow"] == "deep-research"
