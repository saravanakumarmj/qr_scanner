from datetime import datetime, timedelta

from config import DEVICE_ID
from cloud.repository import cloud_get_recent_scan_records
from services.developer_configuration_service import DeveloperConfiguration
from services.recent_scan_cache import recent_scan_cache


def populate_recent_cache():

    recent_scan_cache.clear()

    cache_cleanup_interval_secs = (
        DeveloperConfiguration.cache_cleanup_interval_secs
    )

    cutoff_timestamp = (
        datetime.now()
        - timedelta(seconds=cache_cleanup_interval_secs)
    ).isoformat(timespec="seconds")

    success, records, message = (
        cloud_get_recent_scan_records(
            DEVICE_ID,
            cutoff_timestamp
        )
    )

    if not success:
        return False, message

    recent_scan_cache.load(records)

    return (
        True,
        f"Recent scan cache loaded: "
        f"{recent_scan_cache.size()} QR codes."
    )