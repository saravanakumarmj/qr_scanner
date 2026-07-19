import uuid

from config import DEVICE_ID

from database.repository import (
    local_insert_transaction
)

from utils.datetime_utils import current_timestamp
import uuid


transaction = {

    "transaction_id": str(uuid.uuid4()),

    "qr_code": "250217S0001",

    "device_id": DEVICE_ID,

    "scan_ts": current_timestamp(),

    "cycle_count": 1,

    "scan_result": "SUCCESS",

    "event_reason": None,

    "result_code": "SUCCESS"

}

success, message = local_insert_transaction(transaction)

print()

print(success)

print(message)