from src.silver import create_silver_records


def test_create_silver_records():
    bronze_record = {
        "batch_id": "20260905T093000+0200",
        "ingested_at": "2026-09-05T09:30:00+02:00",
        "data": {
            "base_code": "SEK",
            "conversion_rates": {
                "EUR": 0.09,
                "USD": 0.10,
            },
        },
    }

    result = create_silver_records(bronze_record)

    # The conversion_rates mapping is flattened into one row per
    # currency. Python dict insertion order is preserved, so the first
    # record corresponds to EUR in this test input.
    assert len(result) == 2
    assert result[0]["batch_id"] == "20260905T093000+0200"
    assert result[0]["base_currency"] == "SEK"
    assert result[0]["target_currency"] == "EUR"
    assert result[0]["exchange_rate"] == 0.09