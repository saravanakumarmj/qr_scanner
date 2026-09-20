"""
repository.py

Cloud database operations.

Author : Saravanakumar MJ
Project : QR Scanner
"""

from cloud.connection import get_client

from supabase import create_client

from config import (
    SUPABASE_URL,
    SUPABASE_KEY
)



def get_device(device_id):
    """
    Returns the device information from Supabase.

    Returns
    -------
    (success, device, message)
    """

    try:

        client = get_client()

        response = (
            client.table("qr_device")
            .select("*")
            .eq("device_id", device_id)
            .limit(1)

            .execute()
        )

        if len(response.data) == 0:
            return (
                False,
                None,
                "Device is not registered."
            )

        device = response.data[0]

        return (
            True,
            device,
            "Device validated successfully."
        )

    except Exception as ex:

        return (
            False,
            None,
            str(ex)
        )


# --------------------------------------------------------
# Subscription Validation
# --------------------------------------------------------

def get_subscription_for_device(device_id):
    """
    Get and validate the subscription assigned to a device.

    The subscription is stored only in Supabase and is the
    source of truth for device authorization.

    Returns
    -------
    (success, subscription, message)
    """

    try:

        client = get_client()

        # ------------------------------------------------
        # Get device
        # ------------------------------------------------

        response = (
            client.table("qr_device")
            .select("device_id, subscription_id")
            .eq("device_id", device_id)
            .limit(1)
            .execute()
        )

        if len(response.data) == 0:

            return (
                False,
                None,
                "Device is not registered."
            )

        device = response.data[0]

        subscription_id = device.get("subscription_id")

        if not subscription_id:

            return (
                False,
                None,
                "Device has no subscription assigned."
            )

        # ------------------------------------------------
        # Get subscription
        # ------------------------------------------------

        response = (
            client.table("qr_subscription")
            .select("*")
            .eq("subscription_id", subscription_id)
            .limit(1)
            .execute()
        )

        if len(response.data) == 0:

            return (
                False,
                None,
                f"Subscription {subscription_id} not found."
            )

        subscription = response.data[0]

        # ------------------------------------------------
        # Validate subscription
        # ------------------------------------------------

        from datetime import date

        today = date.today()

        status = subscription.get("status")
        start_date = subscription.get("start_date")
        expiry_date = subscription.get("expiry_date")

        if status != "ACTIVE":

            subscription["valid"] = False
            subscription["message"] = (
                f"Subscription {subscription_id} is {status}."
            )

            return (
                True,
                subscription,
                subscription["message"]
            )

        if start_date and today.isoformat() < start_date:

            subscription["valid"] = False
            subscription["message"] = (
                f"Subscription {subscription_id} "
                f"is not active yet."
            )

            return (
                True,
                subscription,
                subscription["message"]
            )

        if expiry_date and today.isoformat() > expiry_date:

            subscription["valid"] = False
            subscription["message"] = (
                f"Subscription {subscription_id} "
                f"has expired."
            )

            return (
                True,
                subscription,
                subscription["message"]
            )

        # ------------------------------------------------
        # Valid
        # ------------------------------------------------

        subscription["valid"] = True
        subscription["message"] = (
            "Subscription is valid."
        )

        return (
            True,
            subscription,
            "Subscription validated successfully."
        )

    except Exception as ex:

        return (
            False,
            None,
            str(ex)
        )

# --------------------------------------------------------
# Lookup QR
# --------------------------------------------------------

def lookup_qr(qr_code):
    """
    Returns a QR Master record.

    Returns
    -------
    success, qr, message
    """

    try:

        client = get_client()

        response = (
            client.table("qr_master")
            .select("*")
            .eq("qr_code", qr_code)
            .limit(1)
            .execute()
        )

        if len(response.data) == 0:
            return (
                False,
                None,
                "QR Code not found."
            )

        return (
            True,
            response.data[0],
            ""
        )

    except Exception as ex:

        return (
            False,
            None,
            str(ex)
        )



_supabase = None


def cloud_connect():
    """
    Returns a singleton Supabase client.
    """

    global _supabase

    if _supabase is None:

        _supabase = create_client(
            SUPABASE_URL,
            SUPABASE_KEY
        )

    return _supabase

def cloud_insert_transactions(transactions):
    """
    Bulk insert qr_transaction records into Supabase.

    The local-only 'synced' column is intentionally excluded.
    """

    try:

        if not transactions:

            return (
                True,
                "No transactions to upload."
            )

        supabase = cloud_connect()

        payload = []

        for record in transactions:

            payload.append(
                {
                    "transaction_id": record["transaction_id"],
                    "qr_code": record["qr_code"],
                    "device_id": record["device_id"],
                    "scan_ts": record["scan_ts"],
                    "cycle_count": record["cycle_count"],
                    "scan_result": record["scan_result"],
                    "event_reason": (
                        record.get("event_reason")
                        if record.get("event_reason") != "NORMAL_SCAN"
                        else None
                    ),
                    "result_code": record["result_code"]
                }
            )

        supabase.table(
            "qr_transaction"
        ).upsert(
            payload
        ).execute()

        return (
            True,
            f"{len(payload)} transaction(s) uploaded."
        )

    except Exception as ex:

        return (
            False,
            str(ex)
        )

def cloud_insert_invalid_qr(invalid_records):
    """
    Bulk insert qr_invalid records into Supabase.

    The local-only 'synced' column is intentionally excluded.
    """

    try:

        if not invalid_records:

            return (
                True,
                "No invalid QR records to upload."
            )

        supabase = cloud_connect()

        payload = []

        for record in invalid_records:

            payload.append(
                {
                    "invalid_id": record["invalid_id"],
                    "raw_code": record["raw_code"],
                    "device_id": record["device_id"],
                    "scan_ts": record["scan_ts"],
                    "result_code": record["result_code"]
                }
            )

        supabase.table(
            "qr_invalid"
        ).upsert(
            payload
        ).execute()

        return (
            True,
            f"{len(payload)} invalid QR record(s) uploaded."
        )

    except Exception as ex:

        return (
            False,
            str(ex)
        )


def cloud_update_qr_master(qr_records):
    """
    Bulk update qr_master records in Supabase.

    Local-only synchronization fields are intentionally excluded:
        - cloud_synced
        - qr_code_encoded
    """

    try:

        if not qr_records:

            return (
                True,
                "No qr_master records to update."
            )

        supabase = cloud_connect()

        payload = []

        for qr in qr_records:

            payload.append(
                {
                    "qr_code": qr["qr_code"],
                    "cycle_count": qr["cycle_count"],
                    "qr_printed_ts": qr["qr_printed_ts"],
                    "flagged": qr["flagged"],
                    "flag_reason": qr.get("flag_reason"),
                    "flag_mode": qr.get("flag_mode"),
                    "flag_device_id": qr.get("flag_device_id"),
                    "flagged_ts": qr.get("flagged_ts"),
                    "active_status": qr["active_status"],
                    "discard_user": qr.get("discard_user"),
                    "discard_device_id": qr.get("discard_device_id"),
                    "discard_reason": qr.get("discard_reason"),
                    "discard_ts": qr.get("discard_ts"),
                    "created_ts": qr["created_ts"],
                    "updated_ts": qr["updated_ts"],
                    "updated_by": qr["updated_by"]
                }
            )

        supabase.table(
            "qr_master"
        ).upsert(
            payload
        ).execute()

        return (
            True,
            f"{len(payload)} qr_master record(s) updated."
        )

    except Exception as ex:

        return (
            False,
            str(ex)
        )

# ---------------------------------------------------------
# Get Complete QR Master
# ---------------------------------------------------------

def cloud_get_all_qr_master():
    """
    Fetch the complete qr_master table from Supabase.

    Returns
    -------
    success : bool
    data : list[dict] | str
    """

    try:

        supabase = cloud_connect()

        response = (
            supabase
            .table("qr_master")
            .select("*")
            .order("qr_code")
            .execute()
        )

        return (
            True,
            response.data
        )

    except Exception as ex:

        return (
            False,
            str(ex)
        )


def cloud_get_recent_scan_records(device_id, cutoff_timestamp):
    """
    Downloads recent scan records for a device.

    Returns
    -------
    success : bool
    records : list
        Each record contains only:
        qr_code
        scan_ts
    message : str
    """

    try:
        client = get_client()

        # ---------------------------------------------
        # Valid transactions
        # ---------------------------------------------

        transaction_response = (
            client
            .table("qr_transaction")
            .select("qr_code, scan_ts")
            .eq("device_id", device_id)
            .gte("scan_ts", cutoff_timestamp)
            .order("scan_ts", desc=False)
            .execute()
        )

        records = []

        for row in transaction_response.data:
            records.append({
                "qr_code": row["qr_code"],
                "scan_ts": row["scan_ts"]
            })

        # ---------------------------------------------
        # Invalid QR records
        # ---------------------------------------------

        invalid_response = (
            client
            .table("qr_invalid")
            .select("raw_code, scan_ts")
            .eq("device_id", device_id)
            .gte("scan_ts", cutoff_timestamp)
            .order("scan_ts", desc=False)
            .execute()
        )

        for row in invalid_response.data:
            records.append({
                "qr_code": row["raw_code"],
                "scan_ts": row["scan_ts"]
            })

        # ---------------------------------------------
        # Sort combined records by timestamp
        # ---------------------------------------------

        records.sort(
            key=lambda record: record["scan_ts"]
        )

        return (
            True,
            records,
            "Recent scan records downloaded successfully."
        )

    except Exception as ex:

        return (
            False,
            [],
            str(ex)
        )
        
# ---------------------------------------------------------
# Get Incremental QR Master Updates
# ---------------------------------------------------------

def cloud_get_qr_master_updates(last_sync_ts, device_id):
    """
    Fetch qr_master records changed in Supabase after the
    last successful synchronization.

    Only records changed by other devices are returned.

    Parameters
    ----------
    last_sync_ts : str
        Timestamp of the last successful cloud -> local sync.

    device_id : str
        Current Raspberry Pi device ID.

    Returns
    -------
    success : bool
    data : list[dict] | str
    """

    try:

        supabase = cloud_connect()

        response = (
            supabase
            .table("qr_master")
            .select("*")
            .gt("updated_ts", last_sync_ts)
            .neq("updated_by", device_id)
            .order("updated_ts")
            .execute()
        )

        return (
            True,
            response.data
        )

    except Exception as ex:

        return (
            False,
            str(ex)
        )