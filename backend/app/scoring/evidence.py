import re


METRIC_PATTERN = re.compile(r"(\d+(\.\d+)?\s*(%|倍|x|ms|毫秒|qps|rps))", re.IGNORECASE)
LEADERSHIP_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"主导",
        r"负责架构",
        r"架构设计",
        r"生产级",
        r"production[-\s]?grade",
        r"led\b",
        r"architected\b",
    ]
]


def find_resume_evidence(skill: str, resume_profile: dict) -> list[str]:
    evidence = resume_profile.get("evidence", {})
    values = evidence.get(skill, [])
    if isinstance(values, list):
        return values
    if isinstance(values, str):
        return [values]
    return []


def _claim_supported(suggestion: str, resume_text: str) -> bool:
    normalized_resume = resume_text.lower()
    tokens = [token for token in re.split(r"\W+", suggestion.lower()) if len(token) >= 4]
    return any(token in normalized_resume for token in tokens)


def assess_integrity_risk(suggestion: str, resume_text: str) -> dict:
    risk_codes: list[str] = []

    if METRIC_PATTERN.search(suggestion) and not METRIC_PATTERN.search(resume_text):
        risk_codes.append("unsupported_metric")

    has_leadership_claim = any(pattern.search(suggestion) for pattern in LEADERSHIP_PATTERNS)
    resume_supports_leadership = any(pattern.search(resume_text) for pattern in LEADERSHIP_PATTERNS)
    if has_leadership_claim and not resume_supports_leadership:
        risk_codes.append("unsupported_leadership_claim")

    if suggestion.strip() and not risk_codes and not _claim_supported(suggestion, resume_text):
        risk_codes.append("weak_evidence")

    risk_level = "low"
    if any(code.startswith("unsupported_") for code in risk_codes):
        risk_level = "high"
    elif risk_codes:
        risk_level = "medium"

    return {
        "risk_level": risk_level,
        "risk_codes": risk_codes,
        "explanation": "建议包含无法从原简历验证的表述。" if risk_codes else "建议与原简历证据一致。",
    }
