
"""Rule-based priority assignment for IT support tickets."""

def assign_priority(title: str, description: str) -> str:
    """
    Assign a priority based on issue severity and business impact.

    Priority order: Critical > High > Low > Medium (default).
    """

    text = f"{title} {description}".lower()

    # Critical: major outages or serious security incidents
    critical_keywords = [
        "security breach",
        "data breach",
        "ransomware",
        "entire system down",
        "complete system outage",
        "company-wide outage",
        "production outage",
        "all systems down",
        "critical server outage",
    ]

    if any(keyword in text for keyword in critical_keywords):
        return "Critical"

    # High: multiple users or important services affected
    high_keywords = [
        "multiple users affected",
        "entire department",
        "business critical",
        "server unavailable",
        "service unavailable",
        "production system unavailable",
        "office network down",
        "team cannot access",
        "many employees affected",
    ]

    if any(keyword in text for keyword in high_keywords):
        return "High"

    # Low: minor issues and general assistance requests
    low_keywords = [
        "minor issue",
        "cosmetic issue",
        "general inquiry",
        "how to",
        "feature request",
        "font size",
        "display alignment",
    ]

    if any(keyword in text for keyword in low_keywords):
        return "Low"

    # Default priority for other issues
    return "Medium"
