
from tools import validate_analysis


def analyze_complaint(complaint, location=""):
    """Analyze a campus complaint locally, without an API or model."""
    result = validate_analysis(
        data={},
        complaint=complaint,
        location=location,
    )
    result["ai_mode"] = "Offline rule-based decision engine"
    return result
