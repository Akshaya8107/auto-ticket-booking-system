from .schemas import ClassificationResult

RULES = [
    ("Network", "Wi-Fi", ["wifi", "wi-fi", "wireless", "network", "internet", "connectivity"]),
    ("Hardware", "Projector", ["projector", "hardware", "display", "screen not working"]),
    ("Access", "Forgot Password", ["password", "forgot password", "login", "log in", "account access"]),
    ("Performance", "Slow Computer", ["slow", "hanging", "hang", "freezing", "slow computer", "performance"]),
]

def classify(short_description: str, description: str = "") -> ClassificationResult:
    text = f"{short_description} {description}".lower()
    scores = []
    for category, subcategory, keywords in RULES:
        matched = [k for k in keywords if k in text]
        if matched:
            # More specific multi-word matches get a small bonus.
            score = sum(2 if " " in k or "-" in k else 1 for k in matched)
            scores.append((score, category, subcategory, matched))
    if not scores:
        return ClassificationResult(
            category=None, subcategory=None, matched_keywords=[], confidence=0.0,
            reason="No configured classification keyword was found."
        )
    scores.sort(reverse=True)
    score, category, subcategory, matched = scores[0]
    confidence = min(0.99, 0.70 + 0.08 * (score - 1))
    return ClassificationResult(
        category=category, subcategory=subcategory, matched_keywords=matched,
        confidence=round(confidence, 2),
        reason=f"Matched configured keyword(s): {', '.join(matched)}."
    )
