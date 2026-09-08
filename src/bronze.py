from datetime import datetime
from zoneinfo import ZoneInfo


def create_bronze_record(data):
    stockholm = ZoneInfo("Europe/Stockholm")

    source_updated_at = datetime.fromtimestamp(
        data["time_last_update_unix"],
        tz=stockholm,
    )

    ingested_at = datetime.now(stockholm)

    return {
        "batch_id": source_updated_at.strftime("%Y%m%dT%H%M%S%z"),
        "source_updated_at": source_updated_at.isoformat(),
        "ingested_at": ingested_at.isoformat(),
        "data": data,
    }