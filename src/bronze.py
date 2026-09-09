"""
Create bronze-stage records.

The bronze stage preserves the raw API payload and wraps it with
ingestion metadata and a deterministic `batch_id` derived from the
source's last-update timestamp.
"""

from datetime import datetime
from zoneinfo import ZoneInfo


def create_bronze_record(data):
    """Wrap a raw API payload in a bronze record.

    Args:
        data (dict): Raw JSON payload returned by the exchange-rate API.
            Must include the `time_last_update_unix` key (POSIX seconds).

    Returns:
        dict: A bronze record with the following keys:
            - `batch_id`: deterministic ID based on the source timestamp
            - `source_updated_at`: ISO timestamp from the source
            - `ingested_at`: ISO timestamp when the pipeline ingested the data
            - `data`: the original raw payload

    Notes:
        Europe/Stockholm is used explicitly so timestamps are consistent
        regardless of which machine runs the pipeline.
    """
    # Use an explicit named timezone so timestamps are represented
    # consistently across different machines running the pipeline.
    stockholm = ZoneInfo("Europe/Stockholm")

    source_updated_at = datetime.fromtimestamp(
        data["time_last_update_unix"],
        tz=stockholm,
    )

    ingested_at = datetime.now(stockholm)

    # `batch_id` is generated from the source timestamp so repeated runs
    # for the same source update will produce the same id (idempotency).
    return {
        "batch_id": source_updated_at.strftime("%Y%m%dT%H%M%S%z"),
        "source_updated_at": source_updated_at.isoformat(),
        "ingested_at": ingested_at.isoformat(),
        "data": data,
    }