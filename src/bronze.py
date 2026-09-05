from datetime import datetime
from zoneinfo import ZoneInfo


def create_bronze_record(data):
    stockholm = ZoneInfo("Europe/Stockholm")
    now = datetime.now(stockholm)

    return {
        "batch_id": now.strftime("%Y%m%dT%H%M%S%z"),
        "ingested_at": now.isoformat(),
        "data": data,
    }

