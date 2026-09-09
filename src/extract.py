"""
Extraction logic for the exchange rates API.

This module is responsible for performing the HTTP GET to the external
exchange-rate API. The API key must be provided via the
`EXCHANGE_RATE_API_KEY` environment variable (optionally loaded from a
`.env` file during development).
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()


def extract():
    """Fetch latest exchange rates for SEK from the external API.

    Raises:
        ValueError: If the `EXCHANGE_RATE_API_KEY` environment variable is not set.
        requests.HTTPError: If the API returns an unsuccessful HTTP status.

    Returns:
        dict: Parsed JSON response from the exchange-rate API.
    """
    api_key = os.getenv("EXCHANGE_RATE_API_KEY")

    if not api_key:
        raise ValueError("API key not found. Please set the EXCHANGE_RATE_API_KEY environment variable.")

    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/SEK"

    response = requests.get(url)
    # Raise an exception instead of allowing an unsuccessful API
    # response to continue through the pipeline.
    response.raise_for_status()

    return response.json()