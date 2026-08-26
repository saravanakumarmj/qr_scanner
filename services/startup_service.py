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
        pass

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
            ("Configuration", self._load_configuration())
        )

        results.append(
            ("Startup Sync", self._startup_sync())
        )

        results.append(
            ("QR Scanner", self._check_scanner())
        )

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

    def _load_configuration(self):

        print("Downloading application configuration...")

        success, configuration, message = cloud_get_configuration()

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

        print("Startup sync not implemented yet.")

        return False


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
