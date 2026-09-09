import sqlite3

import pytest

from src import load


def test_create_tables(tmp_path, monkeypatch):
    test_db = tmp_path / "test.db"

    # Point the module-level DATABASE_PATH to a temporary file so
    # the created tables live in an isolated test database.
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


def test_load_batch(tmp_path, monkeypatch):
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

    # Persist both the bronze envelope and the flattened silver rows.
    # We will inspect the raw_json stored for the bronze row and the
    # explicit silver rows to ensure both were written.
    load.load_batch(bronze_record, silver_records)

    with sqlite3.connect(test_db) as connection:
        bronze_result = connection.execute(
            """
            SELECT batch_id, ingested_at, raw_json
            FROM bronze_exchange_rates
            """
        ).fetchone()

        silver_results = connection.execute(
            """
            SELECT base_currency, target_currency, exchange_rate
            FROM silver_exchange_rates
            ORDER BY target_currency
            """
        ).fetchall()

    assert bronze_result[0] == "20260908T120000+0200"
    assert bronze_result[1] == "2026-09-08T12:00:00+02:00"
    assert '"base_code": "SEK"' in bronze_result[2]

    assert len(silver_results) == 2
    assert ("SEK", "EUR", 0.091) in silver_results
    assert ("SEK", "USD", 0.106) in silver_results


def test_load_batch_rolls_back_on_error(tmp_path, monkeypatch):
    test_db = tmp_path / "test.db"
    monkeypatch.setattr(load, "DATABASE_PATH", test_db)

    load.create_tables()

    bronze_record = {
        "batch_id": "20260908T120000+0200",
        "ingested_at": "2026-09-08T12:00:00+02:00",
        "data": {
            "base_code": "SEK",
        },
    }

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
            "target_currency": "EUR",
            "exchange_rate": 0.092,
        },
    ]

    # The two silver records intentionally use the same
    # (batch_id, target_currency) to violate the composite primary key
    # and trigger an IntegrityError. The database operations should
    # be transactional and roll back, leaving no rows persisted.
    with pytest.raises(sqlite3.IntegrityError):
        load.load_batch(bronze_record, silver_records)

    with sqlite3.connect(test_db) as connection:
        bronze_count = connection.execute(
            "SELECT COUNT(*) FROM bronze_exchange_rates"
        ).fetchone()[0]

        silver_count = connection.execute(
            "SELECT COUNT(*) FROM silver_exchange_rates"
        ).fetchone()[0]

    assert bronze_count == 0
    assert silver_count == 0