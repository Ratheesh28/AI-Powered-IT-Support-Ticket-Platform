
"""The API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Ticket
from app.preprocessing import CATEGORIES
from app.predictor import predictor
from app.priority import assign_priority
from app.recommendation_engine import recommend_articles

from app.schemas import (
    AnalyticsResponse,
    HealthResponse,
    ModelMetricsSummary,
    PredictionResponse,
    RecommendationResponse,
    TicketInput,
    TicketListResponse,
    TicketResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


def _predict_or_422(payload: TicketInput) -> dict:
    """Run the model; turn 'no usable words' into a clear client error."""
    try:
        return predictor.predict(payload.title, payload.description)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/health", response_model=HealthResponse, tags=["system"])
def health(db: Session = Depends(get_db)):
    """Liveness check: is the model loaded and is the database reachable?"""

    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except SQLAlchemyError:
        logger.exception("Health check: database unreachable")
        db_status = "unavailable"

    healthy = db_status == "ok" and predictor.is_loaded

    body = HealthResponse(
        status="ok" if healthy else "degraded",
        model_loaded=predictor.is_loaded,
        database=db_status,
    )

    code = (
        status.HTTP_200_OK
        if healthy
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return JSONResponse(
        status_code=code,
        content=body.model_dump()
    )


@router.post("/predict", response_model=PredictionResponse, tags=["prediction"])
def predict(payload: TicketInput):
    """Classify a ticket WITHOUT saving it."""
    return _predict_or_422(payload)


@router.post(
    "/recommendations",
    response_model=RecommendationResponse,
    tags=["knowledge base"]
)
def get_recommendations(payload: TicketInput):
    """Predict ticket category and recommend relevant KB articles."""

    # Predict ticket category using the existing ML model
    prediction = _predict_or_422(payload)

    # Retrieve matching knowledge base articles
    articles = recommend_articles(
        title=payload.title,
        description=payload.description,
        category=prediction["category"],
        limit=3
    )

    return RecommendationResponse(
        predicted_category=prediction["category"],
        recommendations=articles
    )


@router.post(
    "/tickets",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["tickets"]
)
def create_ticket(payload: TicketInput, db: Session = Depends(get_db)):
    result = _predict_or_422(payload)

    # Assign ticket priority using the rule-based engine
    priority = assign_priority(payload.title, payload.description)

    ticket = Ticket(
        title=payload.title,
        description=payload.description,
        predicted_category=result["category"],
        priority=priority,
        confidence=result["confidence"],
    )

    try:
        db.add(ticket)
        db.commit()
        db.refresh(ticket)

    except SQLAlchemyError:
        db.rollback()
        logger.exception("Failed to save ticket")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save the ticket. Please try again.",
        )

    logger.info(
        "Saved ticket id=%s category=%s",
        ticket.id,
        ticket.predicted_category
    )

    return ticket


@router.get("/tickets", response_model=TicketListResponse, tags=["tickets"])
def list_tickets(
    limit: int = Query(20, ge=1, le=100, description="Page size"),
    offset: int = Query(0, ge=0, description="Rows to skip"),
    category: str | None = Query(
        None,
        description=f"Filter by one of: {', '.join(CATEGORIES)}"
    ),
    db: Session = Depends(get_db),
):
    """List saved tickets, newest first, with simple pagination."""

    if category is not None and category not in CATEGORIES:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown category '{category}'. Valid categories: {CATEGORIES}",
        )

    query = select(Ticket)
    count_query = select(func.count(Ticket.id))

    if category:
        query = query.where(Ticket.predicted_category == category)
        count_query = count_query.where(Ticket.predicted_category == category)

    try:
        total = db.execute(count_query).scalar_one()

        items = db.execute(
            query.order_by(Ticket.id.desc())
            .limit(limit)
            .offset(offset)
        ).scalars().all()

    except SQLAlchemyError:
        logger.exception("Failed to list tickets")

        raise HTTPException(
            status_code=500,
            detail="Could not read tickets from the database."
        )

    return TicketListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=items
    )


@router.get("/analytics", response_model=AnalyticsResponse, tags=["analytics"])
def analytics(db: Session = Depends(get_db)):
    """Aggregate stats over stored tickets, plus saved model test-set metrics."""

    try:
        total = db.execute(
            select(func.count(Ticket.id))
        ).scalar_one()

        overall_avg = db.execute(
            select(func.avg(Ticket.confidence))
        ).scalar_one()

        rows = db.execute(
            select(
                Ticket.predicted_category,
                func.count(Ticket.id),
                func.avg(Ticket.confidence)
            ).group_by(Ticket.predicted_category)
        ).all()

    except SQLAlchemyError:
        logger.exception("Failed to compute analytics")

        raise HTTPException(
            status_code=500,
            detail="Could not compute analytics."
        )

    by_category = {c: 0 for c in CATEGORIES}

    avg_by_category: dict[str, float | None] = {
        c: None for c in CATEGORIES
    }

    for category, count, avg in rows:
        by_category[category] = count
        avg_by_category[category] = round(float(avg), 4)

    metrics = predictor.load_metrics()
    summary = None

    if metrics:
        summary = ModelMetricsSummary(
            accuracy=metrics["accuracy"],
            macro_precision=metrics["macro_precision"],
            macro_recall=metrics["macro_recall"],
            macro_f1=metrics["macro_f1"],
            test_size=metrics["meta"]["test_size"],
            trained_at=metrics["meta"]["trained_at"],
            dataset_note=metrics["meta"]["dataset_note"],
        )

    return AnalyticsResponse(
        total_tickets=total,
        tickets_by_category=by_category,
        average_confidence=(
            round(float(overall_avg), 4)
            if overall_avg is not None
            else None
        ),
        average_confidence_by_category=avg_by_category,
        model_metrics=summary,
    )
