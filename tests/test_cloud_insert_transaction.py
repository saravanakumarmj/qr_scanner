"""
Test : cloud_insert_transactions()

Uploads one transaction to Supabase.
"""

import uuid
from datetime import datetime

from cloud.repository import cloud_insert_transactions


# ---------------------------------------------------------
# Test Data
# ---------------------------------------------------------

transaction = {

    "transaction_id": str(uuid.uuid4()),

    "qr_code": "260611S0008",

    "device_id": "PI001",

    "scan_ts": datetime.now().isoformat(),

    "cycle_count": 5,

    "scan_result": "SUCCESS",

    "event_reason": None,

    "result_code": "S00"

}


# ---------------------------------------------------------
# Execute Test
# ---------------------------------------------------------

print()

print("Testing cloud_insert_transactions()")

print("--------------------------------------")

success, message = cloud_insert_transactions(
    [transaction]
)

print(f"Success : {success}")

print(f"Message : {message}")

print("--------------------------------------")