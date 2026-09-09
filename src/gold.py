import sqlite3

from src.load import DATABASE_PATH


def create_gold_view():
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("""
            CREATE VIEW IF NOT EXISTS gold_exchange_rates AS

            WITH ranked_rates AS (
                SELECT
                    batch_id,
                    ingested_at,
                    base_currency,
                    target_currency,
                    exchange_rate,

                    LAG(exchange_rate) OVER (
                        PARTITION BY base_currency, target_currency
                        ORDER BY ingested_at
                    ) AS previous_rate,

                    ROW_NUMBER() OVER (
                        PARTITION BY base_currency, target_currency
                        ORDER BY ingested_at DESC
                    ) AS row_number

                FROM silver_exchange_rates
            )

            SELECT
                batch_id,
                ingested_at,
                base_currency,
                target_currency,
                exchange_rate AS current_rate,
                previous_rate,

                ROUND(
                    (
                        (exchange_rate - previous_rate)
                        / previous_rate
                    ) * 100,
                    4
                ) AS daily_change_pct

            FROM ranked_rates
            WHERE row_number = 1
        """)