def create_silver_records(bronze_record):
    data = bronze_record["data"]

    base_currency = data["base_code"]
    rates = data["conversion_rates"]

    silver_records = []

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