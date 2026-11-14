"""Train, evaluate and save the ticket classifier.

Run:  python -m ml.train

Pipeline:  raw CSV -> pandas cleaning -> stratified train/test split
           -> TF-IDF + Logistic Regression (one sklearn Pipeline)
           -> metrics on the UNSEEN test set -> joblib model + metrics.json
"""
import json
import logging
from datetime import datetime, timezone

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from app.config import settings
from app.preprocessing import CATEGORIES, clean_dataframe

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("train")

RANDOM_STATE = 42
TEST_SIZE = 0.2


def build_pipeline() -> Pipeline:
    """TF-IDF turns text into numbers; Logistic Regression classifies them.

    Wrapping both in one Pipeline means the exact same vectorizer that was
    fitted on training data is applied at prediction time, and a single
    joblib file contains everything.
    """
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),   # single words and word pairs ("password reset")
                    min_df=2,             # ignore words seen in fewer than 2 tickets
                    sublinear_tf=True,    # dampen very frequent words
                    stop_words="english",
                ),
            ),
            ("clf", LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)),
        ]
    )


def evaluate(pipeline: Pipeline, x_test: pd.Series, y_test: pd.Series) -> dict:
    """Compute every metric from predictions on the held-out test set."""
    y_pred = pipeline.predict(x_test)
    precision, recall, f1, support = precision_recall_fscore_support(
        y_test, y_pred, labels=CATEGORIES, zero_division=0
    )
    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(
        y_test, y_pred, labels=CATEGORIES, average="macro", zero_division=0
    )
    return {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "macro_precision": float(macro_p),
        "macro_recall": float(macro_r),
        "macro_f1": float(macro_f1),
        "per_class": {
            label: {
                "precision": float(precision[i]),
                "recall": float(recall[i]),
                "f1": float(f1[i]),
                "support": int(support[i]),
            }
            for i, label in enumerate(CATEGORIES)
        },
        "confusion_matrix": {
            "labels": CATEGORIES,
            "rows_are": "true label",
            "columns_are": "predicted label",
            "matrix": confusion_matrix(y_test, y_pred, labels=CATEGORIES).tolist(),
        },
        "classification_report": classification_report(
            y_test, y_pred, labels=CATEGORIES, zero_division=0
        ),
    }


def main() -> dict:
    logger.info("Loading dataset from %s", settings.dataset_path)
    raw = pd.read_csv(settings.dataset_path)
    df = clean_dataframe(raw)
    logger.info("Rows: raw=%d, after cleaning=%d", len(raw), len(df))

    # stratify keeps the category proportions the same in train and test
    x_train, x_test, y_train, y_test = train_test_split(
        df["text"],
        df["category"],
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=df["category"],
    )
    logger.info("Train size=%d, test size=%d", len(x_train), len(x_test))

    pipeline = build_pipeline()
    pipeline.fit(x_train, y_train)  # the test set is never used for fitting

    metrics = evaluate(pipeline, x_test, y_test)
    metrics["meta"] = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "dataset": str(settings.dataset_path.name),
        "dataset_note": "SYNTHETIC_DEMO data: scores reflect template-based tickets, not real-world performance.",
        "train_size": int(len(x_train)),
        "test_size": int(len(x_test)),
        "test_size_fraction": TEST_SIZE,
        "random_state": RANDOM_STATE,
    }

    settings.model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, settings.model_path)
    settings.metrics_path.write_text(json.dumps(metrics, indent=2))
    logger.info("Saved model to %s", settings.model_path)
    logger.info("Saved metrics to %s", settings.metrics_path)

    print("\n=== Test-set evaluation ===")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(metrics["classification_report"])
    print("Confusion matrix (rows=true, cols=predicted):")
    print(pd.DataFrame(
        metrics["confusion_matrix"]["matrix"], index=CATEGORIES, columns=CATEGORIES
    ).to_string())
    return metrics


if __name__ == "__main__":
    main()
