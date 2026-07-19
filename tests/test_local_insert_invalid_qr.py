from config import DEVICE_ID

from database.repository import local_insert_invalid_qr

from utils.datetime_utils import current_timestamp
import uuid


invalid_qr = {

    "invalid_id": str(uuid.uuid4()),
    "raw_code": "INVALID_TEST_002",

    "device_id": DEVICE_ID,

    "scan_ts": current_timestamp(),

    "result_code": ""
}


success, message = local_insert_invalid_qr(invalid_qr)

print()
print("Testing local_insert_invalid_qr()")
print("--------------------------------------")
print(f"Success : {success}")
print(f"Message : {message}")
print("--------------------------------------")