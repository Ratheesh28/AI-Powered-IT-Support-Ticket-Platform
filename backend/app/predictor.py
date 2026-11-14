"""Loads the trained joblib pipeline once and turns ticket text into a prediction."""
import json
import logging
from pathlib import Path

import joblib

from app.config import settings
from app.preprocessing import build_ticket_text

logger = logging.getLogger(__name__)


class ModelNotLoadedError(RuntimeError):
    """Raised when a prediction is requested but no trained model file is available."""


class Predictor:
    def __init__(self, model_path: Path, metrics_path: Path) -> None:
        self.model_path = model_path
        self.metrics_path = metrics_path
        self.pipeline = None

    @property
    def is_loaded(self) -> bool:
        return self.pipeline is not None

    def load(self) -> None:
        """Load the model from disk. Never crashes the app if the file is missing."""
        if not self.model_path.exists():
            logger.error(
                "Model file not found at %s. Run `python -m ml.train` first.", self.model_path
            )
            self.pipeline = None
            return
        self.pipeline = joblib.load(self.model_path)
        logger.info("Model loaded from %s", self.model_path)

    def predict(self, title: str, description: str) -> dict:
        if not self.is_loaded:
            raise ModelNotLoadedError(
                "The classification model is not loaded. Train it with `python -m ml.train`."
            )
        text = build_ticket_text(title, description)
        if not text:
            # Cleaning removed everything (e.g. the input was only punctuation).
            raise ValueError("Ticket text contains no usable words after cleaning.")

        probabilities = self.pipeline.predict_proba([text])[0]
        classes = list(self.pipeline.classes_)
        best = int(probabilities.argmax())
        return {
            "category": classes[best],
            "confidence": round(float(probabilities[best]), 4),
            "probabilities": {c: round(float(p), 4) for c, p in zip(classes, probabilities)},
        }

    def load_metrics(self) -> dict | None:
        """Read the evaluation results that train.py saved (never invented here)."""
        if not self.metrics_path.exists():
            return None
        try:
            return json.loads(self.metrics_path.read_text())
        except (json.JSONDecodeError, OSError):
            logger.exception("Could not read metrics file %s", self.metrics_path)
            return None


# One shared instance for the whole app.
predictor = Predictor(settings.model_path, settings.metrics_path)
