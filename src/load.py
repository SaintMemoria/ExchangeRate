"""
Database persistence helpers using SQLite.

This module keeps the storage layer intentionally small: a local
SQLite database is used for simplicity in exercises and local runs.
The schema separates bronze (raw payload) and silver (flattened rates).
"""

import json
import sqlite3

# Central database path shared by the persistence and analytical layers.
DATABASE_PATH = "exchange_rates.db"


def batch_exists(batch_id):
    """Return True if a bronze batch with `batch_id` already exists.

    This is used by the pipeline to achieve idempotency: if the same
    source batch has already been loaded we skip loading again.
    """
    with sqlite3.connect(DATABASE_PATH) as connection:
        result = connection.execute(
            """
            SELECT 1
            FROM bronze_exchange_rates
            WHERE batch_id = ?
            LIMIT 1
            """,
            (batch_id,),
        ).fetchone()

    return result is not None


def create_tables():
    """Create the bronze and silver tables if they do not exist.

    Schema notes:
      - `bronze_exchange_rates` stores the raw JSON payload; `batch_id`
        is the primary key so we only persist one bronze envelope per
        source update.
      - `silver_exchange_rates` stores one row per `target_currency` and
        uses a composite primary key `(batch_id, target_currency)` so the
        same batch cannot contain duplicate rates for the same target.
    """
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS bronze_exchange_rates (
                batch_id TEXT PRIMARY KEY,
                ingested_at TEXT NOT NULL,
                raw_json TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS silver_exchange_rates (
                batch_id TEXT NOT NULL,
                ingested_at TEXT NOT NULL,
                base_currency TEXT NOT NULL,
                target_currency TEXT NOT NULL,
                exchange_rate REAL NOT NULL,
                PRIMARY KEY (batch_id, target_currency)
            )
        """)


def load_batch(bronze_record, silver_records):
    """Persist a Bronze record and its Silver rows in one transaction.

    Both layers use the same SQLite transaction so they are committed
    together. If any insert fails, the transaction is rolled back,
    preventing a partially loaded batch.
    """
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            INSERT INTO bronze_exchange_rates (
                batch_id,
                ingested_at,
                raw_json
            )
            VALUES (?, ?, ?)
            """,
            (
                bronze_record["batch_id"],
                bronze_record["ingested_at"],
                json.dumps(bronze_record["data"]),
            ),
        )

        rows = [
            (
                record["batch_id"],
                record["ingested_at"],
                record["base_currency"],
                record["target_currency"],
                record["exchange_rate"],
            )
            for record in silver_records
        ]

        # Use executemany to insert all silver rows efficiently.
        connection.executemany(
            """
            INSERT INTO silver_exchange_rates (
                batch_id,
                ingested_at,
                base_currency,
                target_currency,
                exchange_rate
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            rows,
        )