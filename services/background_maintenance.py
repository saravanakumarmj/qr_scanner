"""
background_maintenance.py

Runs periodic background maintenance tasks.

Author  : Saravanakumar MJ
Project : QR Scanner
"""

import threading
import time

from services.developer_configuration_service import (
    DeveloperConfiguration
)
from services.clear_recent_cache import clear_recent_cache


class BackgroundMaintenanceThread:

    def __init__(self, cloud_to_local_sync):

        self._stop_event = threading.Event()
        self._thread = None
        self.cloud_to_local_sync = cloud_to_local_sync

    # --------------------------------------------------------
    # Start
    # --------------------------------------------------------

    def start(self):

        if self._thread is not None:
            return

        self._thread = threading.Thread(
            target=self._run,
            name="BackgroundMaintenance",
            daemon=True
        )

        self._thread.start()

        print(
            "Background maintenance started."
        )

    # --------------------------------------------------------
    # Stop
    # --------------------------------------------------------

    def stop(self):

        self._stop_event.set()

        if self._thread is not None:

            self._thread.join(
                timeout=5
            )

        print(
            "Background maintenance stopped."
        )

    # --------------------------------------------------------
    # Run
    # --------------------------------------------------------

    def _run(self):

        background_check_interval_secs = (
            DeveloperConfiguration
            .background_check_interval_secs
        )

        cache_cleanup_interval_secs = (
            DeveloperConfiguration
            .cache_cleanup_interval_secs
        )

        sync_cloud_to_local_interval_secs = (
            DeveloperConfiguration
            .sync_cloud_to_local_interval_secs
        )

        last_cache_cleanup_time = time.monotonic()

        last_cloud_to_local_sync_time = time.monotonic()

        print(
            f"[MAINT] [{time.strftime('%Y-%m-%d %H:%M:%S')}] "
            f"Background maintenance thread running."
        )

        while not self._stop_event.wait(
            background_check_interval_secs
        ):

            current_time = time.monotonic()

            elapsed_time = (
                current_time
                - last_cache_cleanup_time
            )

            print(
                f"[MAINT] [{time.strftime('%Y-%m-%d %H:%M:%S')}] "
                f"Background maintenance check. "
                f"Elapsed={int(elapsed_time)}s | "
                f"Cleanup Interval={cache_cleanup_interval_secs}s"
            )

            if elapsed_time >= cache_cleanup_interval_secs:

                clear_recent_cache()

                last_cache_cleanup_time = current_time

            # -------------------------------------------------
            # Cloud -> Local periodic synchronization
            # -------------------------------------------------

            sync_elapsed_time = (
                current_time
                - last_cloud_to_local_sync_time
            )

            if (
                sync_elapsed_time
                >= sync_cloud_to_local_interval_secs
            ):

                print(
                    f"[MAINT] "
                    f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
                    f"Cloud -> Local sync triggered. "
                    f"Elapsed={int(sync_elapsed_time)}s | "
                    f"Sync Interval="
                    f"{sync_cloud_to_local_interval_secs}s"
                )

                success, message = (
                    self.cloud_to_local_sync.run()
                )

                if success:

                    print(
                        f"[MAINT] Cloud -> Local sync successful: "
                        f"{message}"
                    )

                    last_cloud_to_local_sync_time = (
                        current_time
                    )

                else:

                    print(
                        f"[MAINT] Cloud -> Local sync failed: "
                        f"{message}"
                    )