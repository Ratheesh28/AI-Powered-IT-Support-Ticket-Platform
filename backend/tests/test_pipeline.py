import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest

from app.config import settings
from app.predictor import ModelNotLoadedError, Predictor
from app.preprocessing import CATEGORIES, build_ticket_text, clean_dataframe


@pytest.fixture(scope="module")
def pipeline():
    return joblib.load(settings.model_path)


@pytest.fixture(scope="module")
def metrics():
    return json.loads(Path(settings.metrics_path).read_text())


def test_dataset_is_labelled_as_demo_data():
    df = pd.read_csv(settings.dataset_path)
    assert set(df["data_source"]) == {"SYNTHETIC_DEMO"}
    assert set(df["category"]) == set(CATEGORIES)


def test_cleaned_dataset_has_no_duplicate_texts():
    clean = clean_dataframe(pd.read_csv(settings.dataset_path))
    assert clean["text"].is_unique


def test_pipeline_structure(pipeline):
    assert [name for name, _ in pipeline.steps] == ["tfidf", "clf"]
    assert set(pipeline.classes_) == set(CATEGORIES)


def test_probabilities_are_valid(pipeline):
    text = build_ticket_text("Wifi down", "No internet connection on my floor")
    proba = pipeline.predict_proba([text])[0]
    assert proba.shape == (len(CATEGORIES),)
    assert np.isclose(proba.sum(), 1.0)
    assert ((proba >= 0) & (proba <= 1)).all()


@pytest.mark.parametrize(
    "title, description, expected",
    [
        ("Password reset", "I forgot my password and my account is locked", "Account Access"),
        ("Printer broken", "Paper jam and the printer tray shows an error", "Hardware"),
        ("Outlook crash", "Outlook crashes with an application error when I open mail", "Software"),
        ("VPN problem", "The wifi and internet connection keep dropping, VPN times out", "Network"),
    ],
)
def test_obvious_tickets_are_classified_correctly(pipeline, title, description, expected):
    assert pipeline.predict([build_ticket_text(title, description)])[0] == expected


def test_saved_metrics_are_internally_consistent(metrics):
    """Metrics come from the held-out test set, so every count must add up."""
    test_size = metrics["meta"]["test_size"]
    matrix = np.array(metrics["confusion_matrix"]["matrix"])
    assert matrix.shape == (4, 4)
    assert matrix.sum() == test_size
    assert sum(v["support"] for v in metrics["per_class"].values()) == test_size
    assert 0.0 <= metrics["accuracy"] <= 1.0
    # accuracy must equal the confusion-matrix diagonal over the total
    assert metrics["accuracy"] == pytest.approx(np.trace(matrix) / test_size)


def test_test_split_is_about_twenty_percent(metrics):
    meta = metrics["meta"]
    total = meta["train_size"] + meta["test_size"]
    assert meta["test_size"] / total == pytest.approx(0.2, abs=0.02)


def test_predictor_returns_structured_result():
    p = Predictor(settings.model_path, settings.metrics_path)
    p.load()
    result = p.predict("Locked out", "My account is locked after too many failed login attempts.")
    assert set(result) == {"category", "confidence", "probabilities"}
    assert result["category"] in CATEGORIES
    assert 0.0 <= result["confidence"] <= 1.0


def test_predictor_rejects_text_that_cleans_to_nothing():
    p = Predictor(settings.model_path, settings.metrics_path)
    p.load()
    with pytest.raises(ValueError):
        p.predict("!!!", "???????????")


def test_predictor_without_model_raises(tmp_path):
    p = Predictor(tmp_path / "missing.joblib", tmp_path / "missing.json")
    p.load()  # must not crash
    assert not p.is_loaded
    assert p.load_metrics() is None
    with pytest.raises(ModelNotLoadedError):
        p.predict("Some title", "Some description text")
