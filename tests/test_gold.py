import sqlite3

from src import gold, load


def test_gold_returns_latest_and_previous_rate(tmp_path, monkeypatch):
    test_db = tmp_path / "test.db"

    monkeypatch.setattr(load, "DATABASE_PATH", test_db)
    monkeypatch.setattr(gold, "DATABASE_PATH", test_db)

    load.create_tables()

    silver_records = [
        {
            "batch_id": "20260908",
            "ingested_at": "2026-09-08T10:00:00+02:00",
            "base_currency": "SEK",
            "target_currency": "EUR",
            "exchange_rate": 0.09,
        },
        {
            "batch_id": "20260909",
            "ingested_at": "2026-09-09T10:00:00+02:00",
            "base_currency": "SEK",
            "target_currency": "EUR",
            "exchange_rate": 0.10,
        },
    ]

    load.load_silver(silver_records)
    gold.create_gold_view()

    with sqlite3.connect(test_db) as connection:
        result = connection.execute(
            """
            SELECT current_rate, previous_rate, daily_change_pct
            FROM gold_exchange_rates
            WHERE target_currency = 'EUR'
            """
        ).fetchone()

    assert result[0] == 0.10
    assert result[1] == 0.09
    assert result[2] == 11.1111