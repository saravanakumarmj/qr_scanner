"""
database/repository.py

SQLite Repository Layer

All SQLite operations are implemented here.
"""

import sqlite3

from database.database import get_connection
from config import DEVICE_ID
from utils.datetime_utils import current_timestamp
from database.database import get_connection


# ---------------------------------------------------------
# Local Lookup QR
# ---------------------------------------------------------

def local_lookup_qr(qr_code):
    """
    Lookup QR from local SQLite database.

    Returns
    -------
    success, qr, message
    """

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM qr_master
            WHERE qr_code = ?
            """,
            (qr_code,)
        )

        row = cursor.fetchone()

        if row is None:

            return (
                False,
                None,
                "QR Code not found."
            )

        return (
            True,
            dict(row),
            ""
        )

    except Exception as ex:

        return (
            False,
            None,
            str(ex)
        )




def local_update_qr_after_scan(qr, scan_timestamp):
    """
    Update qr_master after processing a scan.

    Parameters
    ----------
    qr : dict
        Updated QR record after business rule validation.

    scan_timestamp : str
        Common timestamp for the current scan event.

    Returns
    -------
    success : bool
    message : str
    """

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE qr_master
            SET
                cycle_count = ?,
                flagged = ?,
                flag_reason = ?,
                flag_mode = ?,
                flag_device_id = ?,
                flagged_ts = ?,
                updated_ts = ?,
                updated_by = ?,
                cloud_synced = 0
            WHERE
                qr_code = ?
            """,
            (
                qr["cycle_count"],
                qr["flagged"],
                qr["flag_reason"],
                qr["flag_mode"],
                qr["flag_device_id"],
                qr["flagged_ts"],
                scan_timestamp,          # updated_ts
                DEVICE_ID,
                qr["qr_code"]
            )
        )

        conn.commit()

        if cursor.rowcount == 0:
            return False, "QR Code not found."

        return True, "QR updated successfully."

    except Exception as ex:

        return False, str(ex)
        
def local_insert_transaction(transaction):
    """
    Insert a scan transaction into qr_transaction.

    Parameters
    ----------
    transaction : dict

    Returns
    -------
    success : bool
    message : str
    """

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO qr_transaction
            (
                transaction_id,
                qr_code,
                device_id,
                scan_ts,
                cycle_count,
                scan_result,
                event_reason,
                result_code
            )
            VALUES
            (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                transaction["transaction_id"],
                transaction["qr_code"],
                transaction["device_id"],
                transaction["scan_ts"],
                transaction["cycle_count"],
                transaction["scan_result"],
                transaction["event_reason"],
                transaction["result_code"]
            )
        )

        conn.commit()

        return (
            True,
            "Transaction inserted successfully."
        )

    except Exception as ex:

        return (
            False,
            str(ex)
        )        
        
        
def local_insert_invalid_qr(invalid_qr):
    """
    Insert an invalid QR scan into qr_invalid.

    Parameters
    ----------
    invalid_qr : dict

    Returns
    -------
    success : bool
    message : str
    """

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO qr_invalid
            (
                invalid_id,
                raw_code,
                device_id,
                scan_ts,
                result_code
            )
            VALUES
            (?, ?, ?, ?, ?)
            """,
            (
                invalid_qr["invalid_id"],
                invalid_qr["raw_code"],
                invalid_qr["device_id"],
                invalid_qr["scan_ts"],
                invalid_qr["result_code"]
            )
        )

        conn.commit()

        return (
            True,
            "Invalid QR inserted successfully."
        )

    except Exception as ex:

        return (
            False,
            str(ex)
        )


# ---------------------------------------------------------
# Upload Functions
# ---------------------------------------------------------

def local_get_pending_transactions():
    """
    Returns all pending transaction records that have not yet
    been uploaded to Supabase.

    Returns
    -------
    success : bool
    data    : list[dict] | str
    """

    try:

        # Create database connection
        conn = get_connection()

        cursor = conn.cursor()

        # Read pending transactions
        cursor.execute(
            """
            SELECT *
            FROM qr_transaction
            WHERE synced = 0
            ORDER BY scan_ts
            """
        )

        rows = cursor.fetchall()

        # Convert sqlite.Row objects to dictionaries
        return (
            True,
            [dict(row) for row in rows]
        )

    except Exception as ex:

        return (
            False,
            str(ex)
        )


# ---------------------------------------------------------

def local_get_pending_invalid():
    """
    Returns all invalid QR records that have not yet been
    uploaded to Supabase.

    Returns
    -------
    success : bool
    data    : list[dict] | str
    """

    try:

        # Create database connection
        conn = get_connection()

        cursor = conn.cursor()

        # Read pending invalid QR records
        cursor.execute(
            """
            SELECT *
            FROM qr_invalid
            WHERE synced = 0
            ORDER BY scan_ts
            """
        )

        rows = cursor.fetchall()

        # Convert sqlite.Row objects to dictionaries
        return (
            True,
            [dict(row) for row in rows]
        )

    except Exception as ex:

        return (
            False,
            str(ex)
        )


# ---------------------------------------------------------

def local_get_modified_qr_master(earliest_scan_ts):
    """
    Returns all qr_master records modified on or after the
    earliest pending transaction timestamp.

    Parameters
    ----------
    earliest_scan_ts : str

    Returns
    -------
    success : bool
    data    : list[dict] | str
    """

    try:

        # Create database connection
        conn = get_connection()

        cursor = conn.cursor()

        # Read only modified QR records
        cursor.execute(
            """
            SELECT *
            FROM qr_master
            WHERE last_scan >= ?
            ORDER BY last_scan
            """,
            (earliest_scan_ts,)
        )

        rows = cursor.fetchall()

        # Convert sqlite.Row objects to dictionaries
        return (
            True,
            [dict(row) for row in rows]
        )

    except Exception as ex:

        return (
            False,
            str(ex)
        )


# ---------------------------------------------------------

def local_mark_transactions_synced(transaction_ids):
    """
    Marks uploaded transaction records as synced.

    Parameters
    ----------
    transaction_ids : list[str]

    Returns
    -------
    success : bool
    message : str
    """

    try:

        # Nothing to update
        if not transaction_ids:

            return (
                True,
                "No transactions to update."
            )

        conn = get_connection()

        cursor = conn.cursor()

        # Build placeholders dynamically
        placeholders = ",".join(
            ["?"] * len(transaction_ids)
        )

        # Mark transactions as synced
        cursor.execute(
            f"""
            UPDATE qr_transaction
            SET synced = 1
            WHERE transaction_id IN ({placeholders})
            """,
            transaction_ids
        )

        conn.commit()

        return (
            True,
            f"{cursor.rowcount} transaction(s) marked as synced."
        )

    except Exception as ex:

        return (
            False,
            str(ex)
        )


# ---------------------------------------------------------

def local_mark_invalid_synced(invalid_ids):
    """
    Marks uploaded invalid QR records as synced.

    Parameters
    ----------
    invalid_ids : list[str]

    Returns
    -------
    success : bool
    message : str
    """

    try:

        # Nothing to update
        if not invalid_ids:

            return (
                True,
                "No invalid QR records to update."
            )

        conn = get_connection()

        cursor = conn.cursor()

        # Build placeholders dynamically
        placeholders = ",".join(
            ["?"] * len(invalid_ids)
        )

        # Mark invalid QR records as synced
        cursor.execute(
            f"""
            UPDATE qr_invalid
            SET synced = 1
            WHERE invalid_id IN ({placeholders})
            """,
            invalid_ids
        )

        conn.commit()

        return (
            True,
            f"{cursor.rowcount} invalid QR record(s) marked as synced."
        )

    except Exception as ex:

        return (
            False,
            str(ex)
        )
