"""
Pipeline entrypoint.

This module orchestrates a simple ETL run: it ensures the database
schema and analytical view exist, fetches the latest rates, and loads
new batches if they have not been persisted yet.
"""

from src.bronze import create_bronze_record
from src.extract import extract
from src.gold import create_gold_view
from src.load import (
    batch_exists,
    create_tables,
    load_batch,
)
from src.silver import create_silver_records


def main():
    """Run one pipeline iteration.

    Steps:
        1. Ensure the database tables and Gold view exist.
        2. Extract the latest exchange-rate data.
        3. Create the Bronze record and identify the source batch.
        4. Stop if that batch has already been loaded.
        5. Create Silver records and persist the batch transactionally.
    """
    create_tables()
    create_gold_view()

    raw_data = extract()
    bronze_data = create_bronze_record(raw_data)

    # Idempotency guard: do not load the same source batch twice.
    if batch_exists(bronze_data["batch_id"]):
        print("Batch already loaded. Nothing to do.")
        return

    silver_data = create_silver_records(bronze_data)

    load_batch(bronze_data, silver_data)


if __name__ == "__main__":
    main()