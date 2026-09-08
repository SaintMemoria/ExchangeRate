import json
import sqlite3

DATABASE_PATH = "exchange_rates.db"

def batch_exists(batch_id):
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


def load_bronze(bronze_record):
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO bronze_exchange_rates (
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


def load_silver(silver_records):
    rows = []

    for record in silver_records:
        rows.append(
            (
                record["batch_id"],
                record["ingested_at"],
                record["base_currency"],
                record["target_currency"],
                record["exchange_rate"],
            )
        )

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.executemany(
            """
            INSERT OR IGNORE INTO silver_exchange_rates (
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