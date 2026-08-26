"""QR Scanner application entry point."""

from services.startup_service import StartupService


def main() -> None:
    """Start the QR Scanner application."""

    startup = StartupService()

    if not startup.start():
        print("\nApplication is NOT READY.")
        return

    print("\nApplication started successfully.")


if __name__ == "__main__":
    main()