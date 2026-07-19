"""
tests/test_local_update_qr_after_scan.py
"""

from config import DEVICE_ID
import uuid

from database.repository import (
    local_lookup_qr,
    local_update_qr_after_scan
)

from utils.datetime_utils import current_timestamp


# ---------------------------------------------------------
# Test Configuration
# ---------------------------------------------------------

QR_CODE = "250217S0002"

FLAG_TEST = "N"      # Y = Flag Test, N = Normal Scan

scan_context = {

    "transaction_id": str(uuid.uuid4()),

    "scan_timestamp": current_timestamp(),

    "device_id": DEVICE_ID
}

# ---------------------------------------------------------

print("\nLooking up QR...")

success, qr, message = local_lookup_qr(QR_CODE)

if not success:
    print(message)
    exit()

print("\nBefore Update")
print("--------------------------------------")
print(f"Cycle Count    : {qr['cycle_count']}")
print(f"Flagged        : {qr['flagged']}")
print(f"Flag Reason    : {qr['flag_reason']}")
print(f"Flag Mode      : {qr['flag_mode']}")
print(f"Flag Device ID : {qr['flag_device_id']}")
print(f"Updated By     : {qr['updated_by']}")
print(f"Cloud Synced   : {qr['cloud_synced']}")


# ---------------------------------------------------------
# Simulate Scan
# ---------------------------------------------------------

qr["cycle_count"] += 1

if FLAG_TEST.upper() == "Y":

    qr["flagged"] = 1
    qr["flag_reason"] = "CYCLE_LIMIT"
    qr["flag_mode"] = "AUTO"
    qr["flag_device_id"] = DEVICE_ID
    qr["flagged_ts"] = current_timestamp()

else:

    qr["flagged"] = 0
    qr["flag_reason"] = None
    qr["flag_mode"] = None
    qr["flag_device_id"] = None
    qr["flagged_ts"] = None


# ---------------------------------------------------------
# Update
# ---------------------------------------------------------

success, message = local_update_qr_after_scan(
    qr,
    scan_context["scan_timestamp"]
)

print("\nUpdate Status")
print("--------------------------------------")
print(success)
print(message)


# ---------------------------------------------------------
# Read Again
# ---------------------------------------------------------

success, qr, message = local_lookup_qr(QR_CODE)

print("\nAfter Update")
print("--------------------------------------")
print(f"Cycle Count    : {qr['cycle_count']}")
print(f"Flagged        : {qr['flagged']}")
print(f"Flag Reason    : {qr['flag_reason']}")
print(f"Flag Mode      : {qr['flag_mode']}")
print(f"Flag Device ID : {qr['flag_device_id']}")
print(f"Flagged TS     : {qr['flagged_ts']}")
print(f"Updated By     : {qr['updated_by']}")
print(f"Updated TS     : {qr['updated_ts']}")
print(f"Cloud Synced   : {qr['cloud_synced']}")