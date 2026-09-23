"""
tests/test_qr_scanner.py

Standalone test for the USB QR scanner.
"""

from services.qr_scanner import QRScanner


def main():

    print()
    print("----------------------------------------")
    print("QR Scanner Test")
    print("----------------------------------------")

    try:

        scanner = QRScanner()

        print("Scanner detected successfully.")
        print(f"Scanner : {scanner.device.name}")
        print()
        print("Scan a QR code...")
        print("Press Ctrl+C to stop.")
        print()

        while True:

            qr_value = scanner.read_scan()

            print(
                f"QR Scanned : {qr_value}"
            )

    except KeyboardInterrupt:

        print()
        print("Scanner test stopped.")

    except Exception as ex:

        print()
        print(f"Scanner Error : {ex}")

    finally:

        try:
            scanner.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()