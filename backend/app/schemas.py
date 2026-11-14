"""Pydantic models: they validate incoming JSON and shape outgoing JSON.

If a request breaks a rule here, FastAPI automatically answers with HTTP 422
and a message saying which field failed, before any of our code runs.
"""
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

# Whitespace is trimmed first, then the length rules are applied.
Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=200)]
Description = Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=5000)]
Priority = Literal["Critical", "High", "Medium", "Low"]


class TicketInput(BaseModel):
    title: Title = Field(examples=["Cannot connect to VPN"])
    description: Description = Field(
        examples=["The VPN client connects but times out after a minute."]
    )


class PredictionResponse(BaseModel):
    category: str
    confidence: float = Field(description="Model probability for the predicted category, 0 to 1")
    probabilities: dict[str, float] = Field(description="Probability for every category")


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    predicted_category: str
    priority: Priority
    confidence: float
    created_at: datetime


class TicketListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[TicketResponse]


class ModelMetricsSummary(BaseModel):
    accuracy: float
    macro_precision: float
    macro_recall: float
    macro_f1: float
    test_size: int
    trained_at: str
    dataset_note: str


class AnalyticsResponse(BaseModel):
    total_tickets: int
    tickets_by_category: dict[str, int]
    average_confidence: float | None = Field(
        description="Mean model confidence over stored tickets; null when there are none"
    )
    average_confidence_by_category: dict[str, float | None]
    model_metrics: ModelMetricsSummary | None = Field(
        description="Test-set metrics saved at training time (null if the model has not been trained)"
    )


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    database: str

class KnowledgeArticle(BaseModel):
    id: int
    title: str
    category: str
    content: str
    steps: list[str]
    relevance_score: int


class RecommendationResponse(BaseModel):
    predicted_category: str
    recommendations: list[KnowledgeArticle]
