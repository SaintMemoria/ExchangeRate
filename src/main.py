from src.bronze import create_bronze_record
from src.extract import extract
from src.gold import create_gold_view
from src.load import (
    batch_exists,
    create_tables,
    load_bronze,
    load_silver,
)
from src.silver import create_silver_records


def main():
    create_tables()
    create_gold_view()

    raw_data = extract()
    bronze_data = create_bronze_record(raw_data)

    if batch_exists(bronze_data["batch_id"]):
        print("Batch already loaded. Nothing to do.")
        return

    silver_data = create_silver_records(bronze_data)

    load_bronze(bronze_data)
    load_silver(silver_data)


if __name__ == "__main__":
    main()