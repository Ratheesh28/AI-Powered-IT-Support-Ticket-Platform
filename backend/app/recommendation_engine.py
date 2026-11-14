
"""Recommendation engine for matching IT tickets with KB articles."""

from app.knowledge_base import KNOWLEDGE_BASE


def recommend_articles(
    title: str,
    description: str,
    category: str,
    limit: int = 3
) -> list[dict]:
    """
    Find relevant knowledge base articles using category and keyword matching.
    """

    ticket_text = f"{title} {description}".lower()

    scored_articles = []

    for article in KNOWLEDGE_BASE:

        # Only consider articles from the predicted category
        if article["category"] != category:
            continue

        # Count matching keywords
        score = sum(
            1 for keyword in article["keywords"]
            if keyword.lower() in ticket_text
        )

        # Keep articles with at least one matching keyword
        if score > 0:
            scored_articles.append({
                **article,
                "relevance_score": score
            })

    # Sort by relevance score, highest first
    scored_articles.sort(
        key=lambda article: article["relevance_score"],
        reverse=True
    )

    # Return only the requested number of articles
    return scored_articles[:limit]
