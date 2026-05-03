LEVEL_WEIGHTS = {
    "not_mentioned": 0.0,
    "mentioned": 0.3,
    "basic_usage": 0.5,
    "project_practice": 0.75,
    "deep_experience": 1.0,
}


def clamp_score(value: float) -> int:
    return int(round(max(0.0, min(100.0, value))))
