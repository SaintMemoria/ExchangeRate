"""
Transform a Bronze record into Silver exchange-rate records.

The Silver stage flattens the API's conversion-rate mapping into one
row per currency pair and batch. The resulting records are suitable
for relational storage and downstream analytics.
"""


def create_silver_records(bronze_record):
    """Flatten a Bronze record into Silver exchange-rate records.

    Args:
        bronze_record (dict): Bronze record created by
            `create_bronze_record`.

    Returns:
        list[dict]: One record per target currency, preserving the
            batch ID and ingestion timestamp for traceability.
    """
    data = bronze_record["data"]

    base_currency = data["base_code"]
    rates = data["conversion_rates"]

    silver_records = []

    # Flatten the mapping of target_currency -> rate into individual rows.
    for target_currency, rate in rates.items():
        silver_records.append(
            {
                "batch_id": bronze_record["batch_id"],
                "ingested_at": bronze_record["ingested_at"],
                "base_currency": base_currency,
                "target_currency": target_currency,
                "exchange_rate": rate
            }
        )
    return silver_records