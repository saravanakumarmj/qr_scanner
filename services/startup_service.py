"""
startup_service.py

Application startup orchestrator.

This service is responsible for performing all mandatory startup
checks before the QR scanner begins processing scans.
(venv) saravana@Saravana:~/qr_scanner $ python -m tests.test_startup_service

========== APPLICATION STARTUP ==========

Checking database...
Checking internet connectivity...
Checking Supabase connectivity...
Validating device...
Validating subscription...
Loading configuration...
Synchronizing master data...
Checking camera...
Checking QR scanner...
Checking relay...

Application startup completed successfully.

Current Version:
- Structure only
- Individual services will be implemented incrementally
"""

#from database.schema import initialize_database
from database.health import check_database

from cloud.repository import get_device
from config import DEVICE_ID

from cloud.configuration import cloud_get_configuration
from services.background_maintenance import BackgroundMaintenanceThread
from services.populate_recent_cache import populate_recent_cache


from services.app_settings import (
    load_app_settings,
    print_app_settings,
    get_app_setting
)

from services.developer_configuration_service import (
    load_developer_configuration,
    print_developer_configuration
)


from services.configuration_service import (
    load_configuration,
    print_configuration
)

from services.cloud_to_local_periodic_sync_service import (
    CloudToLocalPeriodicSyncService
)


from services.upload_service import UploadService
from services.refresh_local_service import RefreshLocalService

from utils.datetime_utils import current_timestamp


import config
import socket
from cloud.repository import (
    get_device,
    get_subscription_for_device,
)

from services.qr_scanner import QRScanner

from cloud.health import check_supabase


class StartupService:

    def __init__(self):

            self.cloud_to_local_sync = (
                CloudToLocalPeriodicSyncService()
            )

            self.background_maintenance = (
                BackgroundMaintenanceThread(
                    self.cloud_to_local_sync
                )
            )

    def start(self):

        print("\n========== APPLICATION STARTUP ==========\n")

        results = []

        results.append(
            ("Database", self._check_database())
        )

        results.append(
            ("Internet", self._check_internet())
        )

        results.append(
            ("Supabase", self._check_supabase())
        )

        results.append(
            ("Device", self._validate_device())
        )

        results.append(
            ("Subscription", self._validate_subscription())
        )

        results.append(
            ("Local Settings", self._load_app_settings())
        )

        results.append(
            ("Configuration", self._load_configuration())
        )

        results.append(
            ("Developer Config", self._load_developer_configuration())
        )

        results.append(
            ("Startup Sync", self._startup_sync())
        )
        
        results.append(
            ("Recent Scan Cache", self._populate_recent_cache())
        )


        results.append(
            ("QR Scanner", self._check_scanner())
        )

        if all(status for _, status in results):

            self.background_maintenance.start()

        failed = 0

        print("\n========== STARTUP SUMMARY ==========\n")

        for name, status in results:

            print(
                f"{name:<20} : "
                f"{'PASS' if status else 'FAIL'}"
            )

            if not status:
                failed += 1

        if failed > 0:

            print(
                f"\nStartup failed. "
                f"{failed} service(s) failed."
            )

            return False

        print("\nAPPLICATION READY")

        return True

    # ----------------------------------------------------
    # Individual Startup Tasks
    # ----------------------------------------------------


    def _check_database(self):

        print("Checking database...")

        success, message = check_database()
        
        if success:
            print("Database OK")
            return True

        print(message)
        return False 


    def _check_internet(self):

        print("Checking internet connectivity...")

        try:
            socket.create_connection(
                ("8.8.8.8", 53),
                timeout=3
            )

            print("Internet OK")
            return True

        except OSError as ex:

            print(f"Internet unavailable: {ex}")
            return False

    def _check_supabase(self):

        print("Checking Supabase connectivity...")

        success, message = check_supabase()

        if success:
            print("Supabase OK")
            return True

        print(f"Supabase unavailable: {message}")
        return False

    def _validate_device(self):

        print("Validating device...")

        success, device, message = get_device(DEVICE_ID)

        if not success:
            print(f"ERROR : DEVICE_ID  {DEVICE_ID, message}")
            return False

        print("Device validated.")

        print(f"Device ID      : {device['device_id']}")
        print(f"Factory        : {device['factory_site']}")
        print(f"Department     : {device['department']}")
        print(f"Location       : {device['location']}")
        print(f"Status         : {device['status']}")

        return True

    def _validate_subscription(self):

        print("Validating subscription...")

        success, subscription, message = (
            get_subscription_for_device(DEVICE_ID)
        )

        if not success:

            print(f"ERROR : {message}")

            return False

        print(
            f"Subscription ID     : "
            f"{subscription['subscription_id']}"
        )

        print(
            f"Subscription Status : "
            f"{subscription['status']}"
        )

        print(
            f"Start Date          : "
            f"{subscription['start_date']}"
        )

        print(
            f"Expiry Date         : "
            f"{subscription['expiry_date']}"
        )

        if not subscription["valid"]:

            print(
                f"ERROR : {subscription['message']}"
            )

            return False

        print("Subscription valid.")

        return True


    def _load_app_settings(self):

        print("Loading local application settings...")

        success, message = load_app_settings()

        # Detailed warnings are already printed by
        # load_app_settings().
        #
        # Local settings problems should NOT prevent
        # the scanner from starting because defaults
        # are available.

        print_app_settings()

        if not success:
            print(
                f"[STARTUP] WARNING: {message}"
            )

        else:
            print("Local application settings loaded.")

        return True

    def _load_configuration(self):

        print("Downloading application configuration...")

        success, message = load_configuration()

        if not success:
            print(
                f"[STARTUP] Configuration load failed: {message}"
            )
            raise RuntimeError(message)

        print_configuration()

        return True
        
        
    def _load_developer_configuration(self):

        print("Downloading developer configuration...")

        developer_config_version = get_app_setting(
            "developer_config_version"
        )

        if developer_config_version is None:

            print(
                "[STARTUP] Developer configuration version "
                "not found in local settings."
            )

            return False

        print(
            f"Developer Config Version : "
            f"{developer_config_version}"
        )

        success, message = load_developer_configuration(
            developer_config_version
        )

        if not success:

            print(
                f"[STARTUP] Developer configuration "
                f"load failed: {message}"
            )

            return False

        print_developer_configuration()

        return True
        

    def _startup_sync(self):

        print("Synchronizing local data...")

        # -------------------------------------------------
        # Capture ONE timestamp for this startup sync cycle
        # -------------------------------------------------

        sync_timestamp = current_timestamp()

        print(
            f"Sync Timestamp : {sync_timestamp}"
        )

        # -------------------------------------------------
        # Upload pending local records
        # -------------------------------------------------

        print("Uploading pending local records...")

        success, message = UploadService().run(
            sync_timestamp
        )

        if not success:

            print(
                f"ERROR : Startup upload failed: {message}"
            )

            return False

        print(
            f"Upload successful: {message}"
        )

        # -------------------------------------------------
        # Full refresh of local SQLite
        # -------------------------------------------------

        print("Refreshing local SQLite database...")

        success, message = RefreshLocalService().run()

        if not success:

            print(
                f"ERROR : Local refresh failed: {message}"
            )

            return False

        print(
            f"Local refresh successful: {message}"
        )

        self.cloud_to_local_sync.set_last_sync_ts(
            sync_timestamp
        )

        print(
            f"Cloud -> Local sync watermark : "
            f"{sync_timestamp}"
        )

        return True        
        
            
    def _populate_recent_cache(self):

        if get_app_setting("populate_recent_cache") != "YES":
            print(
                "Recent scan cache population disabled."
            )
            return True

        print("Populating recent scan cache...")

        success, message = populate_recent_cache()

        if not success:
            print(
                f"[STARTUP] Recent scan cache population failed: "
                f"{message}"
            )
            return True

        print(message)

        return True
    
        
        
        
    def _check_camera(self):

        print("Checking camera...")

        # TODO

        return True

    def _check_scanner(self):

        print("Checking QR scanner...")

        success, message = QRScanner.check_health()

        if success:
            print("QR scanner OK")
            return True

        print(f"QR scanner unavailable: {message}")
        return False


    def _check_relay(self):

        print("Checking relay...")

        # TODO

        return True

        