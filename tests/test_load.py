import sqlite3

from src import load


def test_create_tables(tmp_path, monkeypatch):
    test_db = tmp_path / "test.db"

    monkeypatch.setattr(load, "DATABASE_PATH", test_db)

    load.create_tables()

    with sqlite3.connect(test_db) as connection:
        tables = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """
        ).fetchall()

    table_names = [table[0] for table in tables]

    assert "bronze_exchange_rates" in table_names
    assert "silver_exchange_rates" in table_names

def test_load_bronze(tmp_path, monkeypatch):
    test_db = tmp_path / "test.db"
    monkeypatch.setattr(load, "DATABASE_PATH", test_db)

    load.create_tables()

    bronze_record = {
        "batch_id": "20260908T120000+0200",
        "ingested_at": "2026-09-08T12:00:00+02:00",
        "data": {
            "base_code": "SEK",
            "conversion_rates": {
                "EUR": 0.091,
                "USD": 0.106,
            },
        },
    }

    load.load_bronze(bronze_record)

    with sqlite3.connect(test_db) as connection:
        result = connection.execute(
            """
            SELECT batch_id, ingested_at, raw_json
            FROM bronze_exchange_rates
            """
        ).fetchone()

    assert result[0] == "20260908T120000+0200"
    assert result[1] == "2026-09-08T12:00:00+02:00"
    assert '"base_code": "SEK"' in result[2]

def test_load_silver(tmp_path, monkeypatch):
    test_db = tmp_path / "test.db"
    monkeypatch.setattr(load, "DATABASE_PATH", test_db)

    load.create_tables()

    silver_records = [
        {
            "batch_id": "20260908T120000+0200",
            "ingested_at": "2026-09-08T12:00:00+02:00",
            "base_currency": "SEK",
            "target_currency": "EUR",
            "exchange_rate": 0.091,
        },
        {
            "batch_id": "20260908T120000+0200",
            "ingested_at": "2026-09-08T12:00:00+02:00",
            "base_currency": "SEK",
            "target_currency": "USD",
            "exchange_rate": 0.106,
        },
    ]

    load.load_silver(silver_records)

    with sqlite3.connect(test_db) as connection:
        results = connection.execute(
            """
            SELECT base_currency, target_currency, exchange_rate
            FROM silver_exchange_rates
            ORDER BY target_currency
            """
        ).fetchall()

    assert len(results) == 2
    assert ("SEK", "EUR", 0.091) in results
    assert ("SEK", "USD", 0.106) in results