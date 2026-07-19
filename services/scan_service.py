"""
scan_service.py

Core business logic for processing QR scans.
"""
import uuid

from config import DEVICE_ID

from utils.datetime_utils import (
    current_timestamp,
    age_in_days
)

from database.repository import (
    local_lookup_qr,
    local_update_qr_after_scan,
    local_insert_transaction,
    local_insert_invalid_qr
)
from services.configuration_service import Configuration

from services.recent_scan_cache import recent_scan_cache

from services.result_codes import (
    S00_SUCCESS,
    F01_CYCLE_LIMIT,
    F02_AGE_LIMIT,
    I01_INVALID_QR,
    E03_DATABASE_ERROR
)
# ---------------------------------------------------------
# Process Scan
# ---------------------------------------------------------

def process_scan(raw_qr):
    """
    Main entry point for processing a scanned QR.

    Parameters
    ----------
    raw_qr : str

    Returns
    -------
    success : bool
    relay : bool
    result_code : str
    message : str
    """

    # -----------------------------------------------------
    # Ignore Empty Scan
    # -----------------------------------------------------

    if raw_qr is None or raw_qr.strip() == "":

        return (
            False,
            False,
            I01,
            "Empty QR received."
        )

    # -----------------------------------------------------
    # Duplicate Check
    # -----------------------------------------------------

    if recent_scan_cache.exists(raw_qr):

        return (
            True,
            False,
            S01,
            "Duplicate scan ignored."
        )

    # -----------------------------------------------------
    # Scan Context
    # -----------------------------------------------------

    scan_context = {

        "transaction_id": str(uuid.uuid4()),

        "scan_timestamp": current_timestamp(),

        "device_id": DEVICE_ID

    }

    # -----------------------------------------------------
    # Validate QR
    # -----------------------------------------------------

    success, qr, message = _validate_qr(raw_qr)

    # -----------------------------------------------------
    # Invalid QR
    # -----------------------------------------------------

    if not success:

        return _process_invalid_qr(
            raw_qr,
            scan_context
        )

    # -----------------------------------------------------
    # Valid QR
    # -----------------------------------------------------

    return _process_valid_qr(
        qr,
        scan_context
    )
    
    


# ---------------------------------------------------------
# Validate QR
# ---------------------------------------------------------

def _validate_qr(raw_qr):
    """
    Validate whether the scanned QR exists in qr_master.

    Parameters
    ----------
    raw_qr : str
        QR code read from scanner.

    Returns
    -------
    success : bool
        True if QR exists in qr_master.

    qr : dict | None
        QR master record if found.

    message : str
        Status message.
    """

    success, qr, message = local_lookup_qr(raw_qr)

    if not success:

        return (
            False,
            None,
            message
        )

    return (
        True,
        qr,
        "QR validated successfully."
    )


# ---------------------------------------------------------
# Process Valid QR
# ---------------------------------------------------------

def _process_valid_qr(
    qr,
    scan_context
):
    """
    Process a valid QR.

    Parameters
    ----------
    qr : dict
        QR master record.

    scan_context : dict
        Contains:
            transaction_id
            scan_timestamp
            device_id

    Returns
    -------
    success : bool
    relay : bool
    result_code : str
    message : str
    """
    print('data -->',qr)
    relay = False

    result_code = S00_SUCCESS

    # -----------------------------------------------------
    # Increment Cycle Count
    # -----------------------------------------------------

    qr["cycle_count"] += 1

    # -----------------------------------------------------
    # Check Cycle Limit
    # -----------------------------------------------------

    if qr["cycle_count"] >= Configuration.max_cycle:

        qr["flagged"] = 1

        qr["flag_reason"] = "CYCLE_LIMIT"

        qr["flag_mode"] = "AUTO"

        qr["flag_device_id"] = DEVICE_ID

        qr["flagged_ts"] = scan_context["scan_timestamp"]

        relay = True

        result_code = F01_CYCLE_LIMIT

    # -----------------------------------------------------
    # Check Age Limit
    # -----------------------------------------------------

    elif age_in_days(qr["qr_printed_ts"]) >= Configuration.max_age_days:

        qr["flagged"] = 1

        qr["flag_reason"] = "AGE_LIMIT"

        qr["flag_mode"] = "AUTO"

        qr["flag_device_id"] = DEVICE_ID

        qr["flagged_ts"] = scan_context["scan_timestamp"]

        relay = True

        result_code = F02_AGE_LIMIT

    # -----------------------------------------------------
    # Normal Scan
    # -----------------------------------------------------

    else:

        qr["flagged"] = 0

        qr["flag_reason"] = None

        qr["flag_mode"] = None

        qr["flag_device_id"] = None

        qr["flagged_ts"] = None

    # -----------------------------------------------------
    # Update QR Master
    # -----------------------------------------------------

    success, message = local_update_qr_after_scan(
        qr,
        scan_context["scan_timestamp"]
    )

    if not success:

        return (
            False,
            False,
            E03_DATABASE_ERROR,
            message
        )

    # -----------------------------------------------------
    # Build Transaction
    # -----------------------------------------------------

    transaction = {

        "transaction_id": scan_context["transaction_id"],

        "qr_code": qr["qr_code"],

        "device_id": scan_context["device_id"],

        "scan_ts": scan_context["scan_timestamp"],

        "cycle_count": qr["cycle_count"],

        "scan_result": "SUCCESS",

        "event_reason": (
            qr["flag_reason"]
            if qr["flag_reason"]
            else "NORMAL_SCAN"
        ),

        "result_code": result_code

    }

    # -----------------------------------------------------
    # Insert Transaction
    # -----------------------------------------------------

    success, message = local_insert_transaction(
        transaction
    )

    if not success:

        return (
            False,
            False,
            E03_DATABASE_ERROR,
            message
        )

    # -----------------------------------------------------
    # Update Recent Scan Cache
    # -----------------------------------------------------

    recent_scan_cache.add(
        qr["qr_code"],
        scan_context["scan_timestamp"]
    )

    # -----------------------------------------------------
    # Completed
    # -----------------------------------------------------

    return (
        True,
        relay,
        result_code,
        "QR processed successfully."
    )

# ---------------------------------------------------------
# Invalid QR Flow
# ---------------------------------------------------------
def _process_invalid_qr(
    raw_qr,
    scan_context
):
    """
    Process an invalid QR.

    Parameters
    ----------
    raw_qr : str

    scan_context : dict

    Returns
    -------
    success : bool
    relay : bool
    result_code : str
    message : str
    """

    # -----------------------------------------------------
    # Build Invalid QR Record
    # -----------------------------------------------------

    invalid_qr = {

        "invalid_id": str(uuid.uuid4()),
        "raw_code": raw_qr,
        "device_id": scan_context["device_id"],
        "scan_ts": scan_context["scan_timestamp"]
    }

    # -----------------------------------------------------
    # Insert Invalid QR
    # -----------------------------------------------------

    success, message = local_insert_invalid_qr(
        invalid_qr
    )

    if not success:

        return (
            False,
            False,
            E03_DATABASE_ERROR,
            message
        )

    # -----------------------------------------------------
    # Add to Recent Scan Cache
    # -----------------------------------------------------

    recent_scan_cache.add(
        raw_qr,
        scan_context["scan_timestamp"]
    )

    # -----------------------------------------------------
    # Completed
    # -----------------------------------------------------

    return (
        True,
        False,
        I01,
        "Invalid QR processed successfully."
    )