from app.scoring.evidence import assess_integrity_risk


def test_unsupported_metric_is_flagged():
    result = assess_integrity_risk("将接口延迟降低 80%，吞吐提升 3 倍", "Built APIs.")

    assert result["risk_level"] == "high"
    assert "unsupported_metric" in result["risk_codes"]


def test_unsupported_leadership_claim_is_flagged():
    result = assess_integrity_risk("主导生产级平台架构设计", "Built APIs.")

    assert result["risk_level"] == "high"
    assert "unsupported_leadership_claim" in result["risk_codes"]


def test_safe_rewrite_is_low_risk():
    resume_text = "Used FastAPI to build internal APIs and wrote tests."
    result = assess_integrity_risk("突出 FastAPI API 开发和测试经验", resume_text)

    assert result["risk_level"] == "low"
    assert result["risk_codes"] == []
