"""
tests/test_scan_service.py
"""

from services.scan_service import process_scan

from services.configuration_service import (
    load_configuration,
    print_configuration
)


success, message = load_configuration()

if not success:
    print(message)
    exit()

print_configuration()


# ---------------------------------------------------------
# Test Configuration
# ---------------------------------------------------------

TEST_CASE = "NORMAL"

TEST_QRS = {

    "NORMAL": "250217S0002",

    "INVALID": "INVALID_QR_12345",

    "EMPTY": ""

}

raw_qr = TEST_QRS[TEST_CASE]

# ---------------------------------------------------------

print("\n----------------------------------------")
print(f"Test Case : {TEST_CASE}")
print("----------------------------------------")

success, relay, result_code, message = process_scan(raw_qr)

print(f"Success     : {success}")
print(f"Relay       : {relay}")
print(f"Result Code : {result_code}")
print(f"Message     : {message}")