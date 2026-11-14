"""Text cleaning shared by training (ml/train.py) and the API (app/predictor.py).

Using ONE cleaning function in both places is important: if training cleaned
text differently from the API, the model would see inputs it was never
trained on ("training/serving skew") and accuracy would silently drop.
"""
import re

import pandas as pd

CATEGORIES = ["Network", "Hardware", "Software", "Account Access"]

_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
_NON_ALNUM_RE = re.compile(r"[^a-z0-9\s]")
_SPACES_RE = re.compile(r"\s+")


def clean_text(text: object) -> str:
    """Lowercase, strip URLs/emails/punctuation, collapse whitespace.

    Alphanumerics are kept on purpose: tokens like "vpn", "0x80070005" or
    "wifi" are strong signals for the classifier.
    """
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return ""
    text = str(text).lower()
    text = _URL_RE.sub(" ", text)
    text = _EMAIL_RE.sub(" ", text)
    text = _NON_ALNUM_RE.sub(" ", text)
    return _SPACES_RE.sub(" ", text).strip()


def build_ticket_text(title: str | None, description: str | None) -> str:
    """Combine title and description into the single string the model reads."""
    return clean_text(f"{title or ''} {description or ''}")


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare a raw tickets DataFrame for training.

    Steps (each one is a typical, defensible data-cleaning step):
      1. keep only rows with a valid category label
      2. build `text` from title + description and clean it
      3. drop rows whose cleaned text is empty
      4. drop duplicate texts so the same ticket cannot land in both the
         train and test split (that would inflate the test score)
    """
    required = {"title", "description", "category"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

    out = df.copy()
    out["category"] = out["category"].astype(str).str.strip()
    out = out[out["category"].isin(CATEGORIES)]
    out["text"] = [
        build_ticket_text(t, d) for t, d in zip(out["title"], out["description"])
    ]
    out = out[out["text"].str.len() > 0]
    out = out.drop_duplicates(subset="text").reset_index(drop=True)
    return out
