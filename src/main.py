from src.bronze import create_bronze_record
from src.extract import extract


def main():
    raw_data = extract()

    bronze_data = create_bronze_record(raw_data)

    print(bronze_data)


if __name__ == "__main__":
    main()