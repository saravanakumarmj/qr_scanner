"""
main_process.py

Main runtime process for the QR Scanner application.

Responsibilities
----------------
1. Start the QR scanner.
2. Process scanned QR codes.
3. Run cloud synchronization in a background thread.

Upload trigger modes
--------------------
TIME
    Trigger only when upload_interval_secs is reached.

COUNT
    Trigger only when:
        transactions + invalid >= upload_batch_size

BOTH
    Trigger when either TIME or COUNT condition is reached.

Important
---------
- The trigger only decides WHEN to check/upload.
- Once triggered, ALL pending records are uploaded.
- QR master records are NOT included in batch count.
- If there are no pending records, upload is not called.
- Every trigger resets the timer.
- Upload failures never stop the scanner.
- After an upload failure, retry using TIME mode only.
"""

import threading
import time
from datetime import datetime, timedelta

#from config import APP_CONFIG
from services.configuration_service import Configuration

from database.repository import local_get_pending_upload_counts
from services.qr_scanner import QRScanner
from services.scan_service import process_scan
from services.upload_service import UploadService
from utils.datetime_utils import current_timestamp


class MainProcess:

    def __init__(self):

        self.scanner = None
        self.running = True

    # ---------------------------------------------------------
    # Logging Timestamp
    # ---------------------------------------------------------

    @staticmethod
    def _timestamp():
        """
        Return current local timestamp for runtime logs.
        """

        return datetime.now().astimezone().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    # ---------------------------------------------------------
    # Main Runtime
    # ---------------------------------------------------------

    def run(self):
        """
        Start the application runtime.
        """

        print("\n========================================")
        print("       APPLICATION PROCESS")
        print("========================================")

        # -----------------------------------------------------
        # Start background upload thread
        # -----------------------------------------------------

        upload_thread = threading.Thread(
            target=self._upload_loop,
            name="CloudUploadThread",
            daemon=True
        )

        upload_thread.start()

        print(
            "[MAIN] Cloud upload thread started."
        )

        # -----------------------------------------------------
        # Start scanner
        # -----------------------------------------------------

        try:

            self.scanner = QRScanner()

            print(
                "[MAIN] QR scanner started."
            )

            print(
                "[MAIN] Waiting for QR scans...\n"
            )

            self._scan_loop()

        except KeyboardInterrupt:

            print(
                "\n[MAIN] Application stopping..."
            )

        except Exception as ex:

            print(
                f"\n[MAIN] Scanner stopped: {ex}"
            )

            raise

        finally:

            self.running = False

            if self.scanner:

                self.scanner.close()

            print(
                "[MAIN] Application stopped."
            )

    # ---------------------------------------------------------
    # QR Scan Loop
    # ---------------------------------------------------------

    def _scan_loop(self):
        """
        Continuously read QR scans and process them.

        This is the main application thread.
        """

        while self.running:

            raw_qr = self.scanner.read_scan()

            if not raw_qr:

                continue

            try:

                success, relay, result_code, message = (
                    process_scan(raw_qr)
                )

                print(
                    f"[SCAN] [{self._timestamp()}] "
                    f"QR={raw_qr} | "
                    f"Result={result_code} | "
                    f"Relay={relay} | "
                    f"{message}"
                )

            except Exception as ex:

                # -------------------------------------------------
                # A single bad scan must not stop the scanner.
                # -------------------------------------------------

                print(
                    f"[SCAN] [{self._timestamp()}] WARNING: "
                    f"Scan processing failed: {ex}"
                )

    # ---------------------------------------------------------
    # Background Upload Loop
    # ---------------------------------------------------------

    def _upload_loop(self):
        """
        Monitor pending local records and trigger cloud uploads.

        The scheduler checks every second.

        TIME
            Trigger only on time.

        COUNT
            Trigger only when transaction + invalid count
            reaches upload_batch_size.

        BOTH
            Trigger when either time or count condition is met.

        After ANY trigger:
            The timer is reset.

        After upload failure:
            Scheduler changes temporarily to TIME retry mode.
        """

        print(
            f"[SYNC] [{self._timestamp()}] "
            "Upload thread started."
        )

        # -----------------------------------------------------
        # Configuration
        # -----------------------------------------------------

        upload_mode = str(
            Configuration.upload_mode
        ).upper()

        upload_interval = int(
            Configuration.upload_interval_secs
        )

        upload_batch_size = int(
            Configuration.upload_batch_size
        )

        print(
            f"[SYNC] [{self._timestamp()}] "
            f"Mode={upload_mode} | "
            f"Interval={upload_interval}s | "
            f"Batch Size={upload_batch_size}"
        )

        # -----------------------------------------------------
        # Timer
        #
        # This is the beginning of the current upload interval.
        # -----------------------------------------------------

        interval_start = time.monotonic()

        # -----------------------------------------------------
        # Retry mode
        #
        # False = normal configured mode
        # True  = TIME-only retry after failure
        # -----------------------------------------------------

        retry_time_mode = False

        # -----------------------------------------------------
        # Main scheduler loop
        # -----------------------------------------------------

        while self.running:

            try:

                # -------------------------------------------------
                # Get pending record counts
                # -------------------------------------------------

                success, counts = (
                    local_get_pending_upload_counts()
                )

                if not success:

                    print(
                        f"[SYNC] [{self._timestamp()}] "
                        "WARNING: Unable to check "
                        f"pending records: {counts}"
                    )

                    time.sleep(1)

                    continue

                qr_master_count = counts["qr_master"]
                transaction_count = counts["transactions"]
                invalid_count = counts["invalid"]

                # Batch is ONLY new scan records
                batch_count = (
                    transaction_count
                    + invalid_count
                )

                total_count = counts["total"]

                # -------------------------------------------------
                # Check trigger conditions
                # -------------------------------------------------

                elapsed = (
                    time.monotonic()
                    - interval_start
                )

                time_trigger = (
                    elapsed >= upload_interval
                )

                count_trigger = (
                    batch_count >= upload_batch_size
                )

                should_trigger = False
                trigger_reason = ""

                # -------------------------------------------------
                # Retry mode
                #
                # After failure, only TIME can trigger.
                # -------------------------------------------------

                if retry_time_mode:

                    if time_trigger:

                        should_trigger = True

                        trigger_reason = (
                            "retry after upload failure"
                        )

                # -------------------------------------------------
                # Normal configured mode
                # -------------------------------------------------

                else:

                    if upload_mode == "TIME":

                        if time_trigger:

                            should_trigger = True

                            trigger_reason = (
                                "time interval reached"
                            )

                    elif upload_mode == "COUNT":

                        if count_trigger:

                            should_trigger = True

                            trigger_reason = (
                                "batch size reached"
                            )

                    elif upload_mode == "BOTH":

                        if count_trigger:

                            should_trigger = True

                            trigger_reason = (
                                "batch size reached"
                            )

                        elif time_trigger:

                            should_trigger = True

                            trigger_reason = (
                                "time interval reached"
                            )

                    else:

                        print(
                            f"[SYNC] [{self._timestamp()}] "
                            "WARNING: Invalid upload mode: "
                            f"{upload_mode}"
                        )

                        time.sleep(1)

                        continue

                # -------------------------------------------------
                # Nothing triggered
                # -------------------------------------------------

                if not should_trigger:

                    time.sleep(1)

                    continue

                # -------------------------------------------------
                # TRIGGER OCCURRED
                # -------------------------------------------------

                if trigger_reason == "time interval reached":

                    trigger_detail = (
                        f"time interval reached : "
                        f"{upload_interval} secs"
                    )

                elif trigger_reason == "batch size reached":

                    trigger_detail = (
                        f"batch size reached : "
                        f"{batch_count} records"
                    )

                else:

                    trigger_detail = (
                        f"{trigger_reason} : "
                        f"{upload_interval} secs"
                    )

                print(
                    f"[SYNC] [{self._timestamp()}] "
                    f"Upload triggered: {trigger_detail}"
                )

                # -------------------------------------------------
                # IMPORTANT
                #
                # Every trigger resets the timer.
                #
                # This happens BEFORE checking whether records
                # exist and regardless of upload success/failure.
                # -------------------------------------------------

                interval_start = time.monotonic()

                # -------------------------------------------------
                # No pending records
                # -------------------------------------------------

                if total_count == 0:

                    print(
                        f"[SYNC] [{self._timestamp()}] "
                        "No pending records to upload."
                    )

                    time.sleep(1)

                    continue

                # -------------------------------------------------
                # Pending record summary
                # -------------------------------------------------

                print(
                    f"[SYNC] [{self._timestamp()}] "
                    f"Pending: "
                    f"QR={qr_master_count} | "
                    f"Tran={transaction_count} | "
                    f"Inv={invalid_count} | "
                    f"Batch={batch_count}"
                )

                # -------------------------------------------------
                # Start upload
                # -------------------------------------------------

                print(
                    f"[SYNC] [{self._timestamp()}] "
                    "Starting cloud upload..."
                )

                sync_timestamp = current_timestamp()

                service = UploadService()

                success, message = service.run(
                    sync_timestamp
                )

                # -------------------------------------------------
                # Upload successful
                # -------------------------------------------------

                if success:

                    print(
                        f"[SYNC] [{self._timestamp()}] "
                        f"SUCCESS: {message}"
                    )

                    # -------------------------------------------------
                    # Return to configured mode after successful
                    # retry.
                    # -------------------------------------------------

                    retry_time_mode = False

                # -------------------------------------------------
                # Upload failed
                # -------------------------------------------------

                else:

                    print(
                        f"[SYNC] [{self._timestamp()}] "
                        f"UPLOAD FAILURE: {message}"
                    )

                    print(
                        f"[SYNC] [{self._timestamp()}] "
                        "Records will be uploaded in the "
                        "next run. Contact admin if the "
                        "problem persists."
                    )

                    # -------------------------------------------------
                    # Prevent COUNT from immediately triggering
                    # repeatedly.
                    # -------------------------------------------------

                    retry_time_mode = True

                    # -------------------------------------------------
                    # Timer was already reset when the trigger
                    # occurred. Keep that reset.
                    # -------------------------------------------------

                time.sleep(1)

            except Exception as ex:

                # -------------------------------------------------
                # Synchronization errors must NEVER stop scanning.
                # -------------------------------------------------

                print(
                    f"[SYNC] [{self._timestamp()}] "
                    "WARNING: Synchronization error: "
                    f"{ex}"
                )

                # -------------------------------------------------
                # Treat unexpected errors as upload failures.
                # -------------------------------------------------

                retry_time_mode = True

                # Every trigger/error cycle gets a fresh retry
                # interval.

                interval_start = time.monotonic()

                time.sleep(1)