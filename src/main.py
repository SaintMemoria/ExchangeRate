from src.bronze import create_bronze_record
from src.extract import extract
from src.silver import create_silver_records


def main():
    raw_data = extract()
    
    bronze_data = create_bronze_record(raw_data)
    silver_data = create_silver_records(bronze_data)

    print(silver_data)


if __name__ == "__main__":
    main()