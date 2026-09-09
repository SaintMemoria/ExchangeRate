"""
exchange_rates package

This package contains a small ETL pipeline that extracts exchange rate
data from an external API, normalizes it into bronze/silver/gold stages,
and persists the results into a local SQLite database for analysis.

Modules:
- `extract` - fetches data from the external API
- `bronze`  - normalizes raw API payloads into a single bronze record
- `silver`  - flattens conversion rates into rows
- `load`    - persists bronze and silver records into SQLite
- `gold`    - creates a read-only view for final analytics
"""
