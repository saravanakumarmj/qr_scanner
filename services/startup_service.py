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

from cloud.configuration import get_configuration
import config


class StartupService:

    def __init__(self):
        pass

    def start(self):

        print("\n========== APPLICATION STARTUP ==========\n")


        results = []

        results.append(("Database", self._check_database()))
        results.append(("Internet", self._check_internet()))
        results.append(("Supabase", self._check_supabase()))
        results.append(("Device", self._validate_device()))
        results.append(("Configuration", self._load_configuration()))
        
 
    #   Phase 2
    #           
    #       results.append(("Startup Sync", self._startup_sync()))
    #       results.append(("Camera", self._check_camera()))
    #       results.append(("QR Scanner", self._check_scanner()))
    #       results.append(("Relay", self._check_relay()))
    #

        failed = 0

        print("\n========== STARTUP SUMMARY ==========\n")

        for name, status in results:
            print(f"{name:<20} : {'PASS' if status else 'FAIL'}")
            if not status:
                failed += 1
 
        if failed > 0:
            print(f"\nStartup failed. {failed} service(s) failed.")
            return False

        print("\nStartup completed successfully.")
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

        # TODO

        return True

    def _check_supabase(self):

        print("Checking Supabase connectivity...")

        # TODO

        return True

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

        # TODO

        return True

    def _load_configuration(self):

        print("Downloading application configuration...")

        success, configuration, message = get_configuration()

        if not success:
            print(f"ERROR : {message}")
            return False

        config.APP_CONFIG.clear()
        config.APP_CONFIG.update(configuration)

        print("Configuration downloaded.")

        print(f"Configuration Version : {configuration['config_version']}")
        print(f"Max Cycle            : {configuration['max_cycle']}")
        print(f"Sync Interval        : {configuration['sync_interval']}")
        print(f"Relay ON Time        : {configuration['relay_on_time']}")

        return True

    def _startup_sync(self):

        print("Synchronizing master data...")

        # TODO

        return True

    def _check_camera(self):

        print("Checking camera...")

        # TODO

        return True

    def _check_scanner(self):

        print("Checking QR scanner...")

        # TODO

        return True

    def _check_relay(self):

        print("Checking relay...")

        # TODO

        return True
