# Exchange Rates ETL (DevOps exercise)

## Purpose

A small Python data-ingestion pipeline created as part of a DevOps course project.

The pipeline retrieves daily SEK exchange rates from ExchangeRate-API, preserves
the source data in a Bronze layer, transforms it into relational Silver records,
stores the data in SQLite, and exposes analytical information through a Gold view.

The project also demonstrates GitHub Flow, automated testing, linting,
GitHub Actions CI, and secure handling of API credentials.

## ExchangeRate API

The pipeline calls the ExchangeRate API v6: `https://v6.exchangerate-api.com/v6/<API_KEY>/latest/SEK`.
The request is performed in `src/extract.py` and requires an
`EXCHANGE_RATE_API_KEY` environment variable (see Setup).

## Architecture (Bronze / Silver / Gold)

- Bronze (`src/bronze.py`): wraps the raw API JSON with metadata into a single
	envelope containing `batch_id`, `source_updated_at`, `ingested_at`,
	and the raw payload. `batch_id` is derived from the source's
	`time_last_update_unix` timestamp to make loads idempotent.
- Silver (`src/silver.py`): flattens the `conversion_rates` mapping into
    one row per currency pair and batch.
- Gold (`src/gold.py`): an SQL view that exposes the most recent rate
	per currency pair alongside the previous rate and a computed
	percentage change from the previous available observation. 
    Window functions (`LAG`, `ROW_NUMBER`) are used for these calculations.

## Persistence and Data Integrity

- SQLite is used for persistence (`exchange_rates.db` by default). The
	schema separates `bronze_exchange_rates` (raw JSON) and
	`silver_exchange_rates` (flattened rows) in `src/load.py`.
- Idempotent batch handling: before loading, the pipeline checks for
	an existing `batch_id` and skips loading if the batch is already
	present (`batch_exists()`). This keeps repeated runs safe.
- Atomic Bronze/Silver loading: `load_batch()` uses a single SQLite
	connection context so inserts are committed together; on
	exceptions the transaction is rolled back, ensuring atomicity.

## Setup

1. Create and activate a Python 3.12 virtual environment (recommended):

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Provide your ExchangeRate API key. Create a `.env` file in the
	 repository root with the following content:

```
EXCHANGE_RATE_API_KEY=your_real_api_key_here
```

## Running the pipeline

- Run a single pipeline iteration locally:

```bash
python -m src.main
```

- Run the test suite with `pytest`:

```bash
python -m pytest
```

- Run the linter (Ruff):

```bash
ruff check .
```

## Continuous Integration (GitHub Actions)

This repository contains two GitHub Actions workflows in
`.github/workflows/`:

- `ci.yml` — runs on `push` and `pull_request`; it installs
	dependencies, runs `ruff`, and executes the `pytest` suite.
- `smoke.yml` — a manually-triggered smoke test (`workflow_dispatch`) to
	exercise the real ExchangeRate API. The smoke test expects the
	`EXCHANGE_RATE_API_KEY` secret to be configured in the repository's
	Secrets (see Manual API smoke test below).

## Manual API smoke test (GitHub Actions)

To run the smoke test from the Actions tab in GitHub:

1. Add `EXCHANGE_RATE_API_KEY` to your repository's Secrets (Settings → Secrets → Actions).
2. Open the `API Smoke Test` workflow and click `Run workflow`.

The workflow runs a small Python snippet that calls `src.extract.extract()`
and asserts the payload shape returned by the real API.

## Branching model

This project follows GitHub Flow:

- Create a short-lived feature branch for each change (e.g. `docs/add-readme`).
- Open a pull request into `main`.
- CI (`ci.yml`) runs on push/PR; merge when green.
- Peer code review was not used because the project was completed individually.

## Notes and testing guidance

- The code is intentionally small and designed for local development
	and CI in a learning environment. The SQLite DB path is configured
	via the module-level `DATABASE_PATH` in `src/load.py` and tests use
	`tmp_path` to isolate temporary databases.
- Tests mock network calls where appropriate; the smoke workflow runs
	a real network call and requires a valid API key in Secrets.

## Architecture diagram

```mermaid
flowchart LR
    A[ExchangeRate API] --> B[Extract]
    B --> C[Bronze]
    C --> D[Silver]
    D --> E[(SQLite)]
    E --> F[Gold View]
