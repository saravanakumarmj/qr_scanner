from datetime import datetime

from services.developer_configuration_service import DeveloperConfiguration
from services.recent_scan_cache import recent_scan_cache


def clear_recent_cache():

    current_timestamp = datetime.now().isoformat(
        timespec="seconds"
    )

    print(
        f"[MAINT] [{current_timestamp}] "
        f"Clearing recent scan cache..."
    )

    cache_cleanup_interval_secs = (
        DeveloperConfiguration.cache_cleanup_interval_secs
    )

    removed_count, cutoff_timestamp = (
        recent_scan_cache.cleanup(
            cache_cleanup_interval_secs
        )
    )

    current_timestamp = datetime.now().isoformat(
        timespec="seconds"
    )

    message = (
        f"Recent scan cache cleared: "
        f"{removed_count} QR codes removed "
        f"up to {cutoff_timestamp}."
    )

    print(
        f"[MAINT] [{current_timestamp}] {message}"
    )

    return True, message