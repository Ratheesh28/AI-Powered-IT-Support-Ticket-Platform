"""Shared test setup.

The environment variables below MUST be set before `app` is imported, because
app.config reads them once at import time. This keeps tests isolated:
  * an in-memory SQLite database (nothing is written to tickets.db)
  * a throwaway model/metrics location (your real trained model is untouched)
"""
import os
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="ticket_tests_"))
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["MODEL_PATH"] = str(_TMP / "ticket_classifier.joblib")
os.environ["METRICS_PATH"] = str(_TMP / "metrics.json")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.config import settings  # noqa: E402
from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.predictor import predictor  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def trained_model():
    """Train a fresh model once per test session into the temp folder."""
    from ml import generate_dataset, train

    if not settings.dataset_path.exists():
        generate_dataset.main()
    train.main()
    predictor.load()
    return settings.model_path


@pytest.fixture()
def client():
    """A test client with an empty database for every test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def valid_ticket():
    return {
        "title": "Cannot connect to VPN",
        "description": "The VPN client connects but times out after a minute.",
    }
