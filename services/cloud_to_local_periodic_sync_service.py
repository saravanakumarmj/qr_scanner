"""
cloud_to_local_periodic_sync_service.py

Performs incremental cloud -> local synchronization
for qr_master.

Only INSERT and UPDATE operations are performed locally.

Author  : Saravanakumar MJ
Project : QR Scanner
"""

from datetime import datetime

from config import DEVICE_ID

from cloud.repository import (
    cloud_get_qr_master_updates
)

from database.repository import (
    local_incremental_refresh_qr_master
)


class CloudToLocalPeriodicSyncService:

    def __init__(self, last_sync_ts=None):

        self.last_sync_ts = last_sync_ts

    # --------------------------------------------------------
    # Set Initial Sync Timestamp
    # --------------------------------------------------------

    def set_last_sync_ts(self, sync_timestamp):

        self.last_sync_ts = sync_timestamp

    # --------------------------------------------------------
    # Get Last Sync Timestamp
    # --------------------------------------------------------

    def get_last_sync_ts(self):

        return self.last_sync_ts

    # --------------------------------------------------------
    # Run Incremental Sync
    # --------------------------------------------------------

    def run(self):

        if self.last_sync_ts is None:

            return (
                False,
                "Last synchronization timestamp is not set."
            )

        # ----------------------------------------------------
        # Fetch cloud changes
        # ----------------------------------------------------

        success, qr_records = (
            cloud_get_qr_master_updates(
                self.last_sync_ts,
                DEVICE_ID
            )
        )

        if not success:

            return (
                False,
                f"Failed to fetch cloud qr_master updates: "
                f"{qr_records}"
            )

        # ----------------------------------------------------
        # Nothing to synchronize
        # ----------------------------------------------------

        if not qr_records:

            return (
                True,
                "No cloud qr_master updates found."
            )

        # ----------------------------------------------------
        # Apply changes locally
        # ----------------------------------------------------

        success, message = (
            local_incremental_refresh_qr_master(
                qr_records
            )
        )

        if not success:

            return (
                False,
                message
            )

        # ----------------------------------------------------
        # Advance watermark only after successful update
        # ----------------------------------------------------

        latest_updated_ts = max(
            qr["updated_ts"]
            for qr in qr_records
        )

        self.last_sync_ts = latest_updated_ts

        return (
            True,
            (
                f"{message} "
                f"Last sync timestamp: "
                f"{self.last_sync_ts}"
            )
        )