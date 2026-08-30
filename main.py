"""
main.py

Application entry point.

Responsibilities:
    1. Run startup validation.
    2. Start the main application process.
"""

from services.startup_service import StartupService
from services.main_process import MainProcess


def main():

    print("\n========================================")
    print("       QR SCANNER APPLICATION")
    print("========================================")

    # -----------------------------------------------------
    # Application Startup
    # -----------------------------------------------------

    startup = StartupService()

    if not startup.start():

        print("\nAPPLICATION NOT STARTED.")

        return

    # -----------------------------------------------------
    # Start Main Application Process
    # -----------------------------------------------------

    process = MainProcess()

    process.run()


if __name__ == "__main__":
    main()
