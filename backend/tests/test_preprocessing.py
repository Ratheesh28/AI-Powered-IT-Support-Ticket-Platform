import numpy as np
import pandas as pd
import pytest

from app.preprocessing import CATEGORIES, build_ticket_text, clean_dataframe, clean_text


def test_clean_text_lowercases_and_strips_punctuation():
    assert clean_text("  Wifi   KEEPS, disconnecting!!! ") == "wifi keeps disconnecting"


def test_clean_text_removes_urls_and_emails():
    out = clean_text("See https://intranet.corp/help or mail me at jo.doe@corp.com now")
    assert "http" not in out and "@" not in out and "corp" not in out
    assert out == "see or mail me at now"


def test_clean_text_keeps_alphanumeric_codes():
    assert "0x80070005" in clean_text("Error 0x80070005 on update")


@pytest.mark.parametrize("value", [None, np.nan, "", "   "])
def test_clean_text_handles_empty_values(value):
    assert clean_text(value) == ""


def test_build_ticket_text_combines_title_and_description():
    assert build_ticket_text("VPN Down", "Cannot connect.") == "vpn down cannot connect"


def test_clean_dataframe_filters_and_deduplicates():
    raw = pd.DataFrame(
        {
            "title": ["VPN down", "VPN down", "Printer jam", "???", "Reset"],
            "description": ["cannot connect", "cannot connect", "tray error", "!!!", "my password"],
            "category": ["Network", "Network", "Hardware", "Software", "Not A Category"],
        }
    )
    clean = clean_dataframe(raw)
    # duplicate removed, empty-text row removed, invalid-category row removed
    assert list(clean["text"]) == ["vpn down cannot connect", "printer jam tray error"]
    assert set(clean["category"]) <= set(CATEGORIES)


def test_clean_dataframe_requires_columns():
    with pytest.raises(ValueError, match="missing required columns"):
        clean_dataframe(pd.DataFrame({"title": ["a"], "description": ["b"]}))
