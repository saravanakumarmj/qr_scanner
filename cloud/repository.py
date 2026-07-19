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

    Parameters
    ----------
    transactions : list[dict]

    Returns
    -------
    success : bool
    message : str
    """

    try:

        if not transactions:

            return (
                True,
                "No transactions to upload."
            )

        supabase = cloud_connect()

        supabase.table(
            "qr_transaction"
        ).insert(
            transactions
        ).execute()

        return (
            True,
            f"{len(transactions)} transaction(s) uploaded."
        )

    except Exception as ex:

        return (
            False,
            str(ex)
        )


def cloud_insert_invalid_qr(invalid_records):
    """
    Bulk insert qr_invalid records.

    Parameters
    ----------
    invalid_records : list[dict]
    """

    try:

        if not invalid_records:

            return (
                True,
                "No invalid QR records."
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
            f"{len(invalid_records)} invalid QR(s) uploaded."
        )

    except Exception as ex:

        return (
            False,
            str(ex)
        )




def cloud_update_qr_master(qr_records):
    """
    Bulk update qr_master records in Supabase.

    Parameters
    ----------
    qr_records : list[dict]

    Returns
    -------
    success : bool
    message : str
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