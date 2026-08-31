import os

import requests
from dotenv import load_dotenv

load_dotenv()

def extract():
    # GET API
    api_key = os.getenv("EXCHANGE_RATE_API_KEY")

    if not api_key:
        raise ValueError("API key not found. Please set the EXCHANGE_RATE_API_KEY environment variable.")

    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/SEK"

    response = requests.get(url)
    response.raise_for_status()

    return response.json()

def transform(data):
    # select/rename/clean fields
    pass

def load(data):
    # write to database
    pass

def main():
    raw = extract()
    transformed = transform(raw)
    load(transformed)
    print(raw)

if __name__ == "__main__":
    main()