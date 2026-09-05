from unittest.mock import Mock

import pytest

from src.main import extract


def test_extract_requires_api_key(monkeypatch):
    monkeypatch.delenv("EXCHANGE_RATE_API_KEY", raising=False)

    with pytest.raises(ValueError):
        extract()


def test_extract_returns_json(monkeypatch):
    monkeypatch.setenv("EXCHANGE_RATE_API_KEY", "fake-key")

    fake_response = Mock()
    fake_response.json.return_value = {
        "base_code": "SEK",
        "conversion_rates": {
            "EUR": 0.09,
            "USD": 0.10
        }
    }

    monkeypatch.setattr(
        "src.extract.requests.get",
        lambda url: fake_response
    )

    result = extract()

    assert result["base_code"] == "SEK"
    assert "conversion_rates" in result