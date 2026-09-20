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
    	       AND active_status = ?
            """,
            (qr_code, True)
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
    #print(" !! Ins Transactrion data",transaction)

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
            "Insert Transaction table : " + str(ex)
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

def local_get_pending_transactions(sync_timestamp):
    """
    Returns pending transaction records that were scanned
    at or before sync_timestamp.

    Records created after sync_timestamp are left for the
    next synchronization cycle.
    """

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM qr_transaction
            WHERE synced = 0
              AND scan_ts <= ?
            ORDER BY scan_ts
            """,
            (sync_timestamp,)
        )

        rows = cursor.fetchall()

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
# Get Pending Invalid QR
# ---------------------------------------------------------

def local_get_pending_invalid(sync_timestamp):
    """
    Returns pending invalid QR records that were scanned
    at or before sync_timestamp.

    Records created after sync_timestamp are left for the
    next synchronization cycle.
    """

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM qr_invalid
            WHERE synced = 0
              AND scan_ts <= ?
            ORDER BY scan_ts
            """,
            (sync_timestamp,)
        )

        rows = cursor.fetchall()

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
# Get Modified QR Master
# ---------------------------------------------------------

def local_get_modified_qr_master(sync_timestamp):
    """
    Returns qr_master records that have local changes
    pending for cloud synchronization.

    Only records modified at or before sync_timestamp
    are included.

    qr_code_encoded is removed before returning the records
    because it is a local-only field.
    """

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                qr_code,
                cycle_count,
                qr_printed_ts,
                flagged,
                flag_reason,
                flag_mode,
                flag_device_id,
                flagged_ts,
                active_status,
                discard_user,
                discard_device_id,
                discard_reason,
                discard_ts,
                created_ts,
                updated_ts,
                updated_by
            FROM qr_master
            WHERE cloud_synced = 0
              AND updated_ts <= ?
            ORDER BY updated_ts
            """,
            (sync_timestamp,)
        )

        rows = cursor.fetchall()

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
# Mark Transactions Synced
# ---------------------------------------------------------

def local_mark_transactions_synced(sync_timestamp):
    """
    Marks all transaction records scanned at or before
    sync_timestamp as synced.

    Records created after sync_timestamp remain pending.
    """

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE qr_transaction
            SET synced = 1
            WHERE synced = 0
              AND scan_ts <= ?
            """,
            (sync_timestamp,)
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
# Mark QR Master Synced
# ---------------------------------------------------------

def local_mark_qr_master_synced(sync_timestamp):
    """
    Marks all qr_master records modified at or before
    sync_timestamp as synced.

    Records modified after sync_timestamp remain pending.
    """

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE qr_master
            SET cloud_synced = 1
            WHERE cloud_synced = 0
              AND updated_ts <= ?
            """,
            (sync_timestamp,)
        )

        conn.commit()

        return (
            True,
            f"{cursor.rowcount} qr_master record(s) marked as synced."
        )

    except Exception as ex:

        return (
            False,
            str(ex)
        )


# ---------------------------------------------------------
# Mark Invalid QR Synced
# ---------------------------------------------------------

def local_mark_invalid_synced(sync_timestamp):
    """
    Marks all invalid QR records scanned at or before
    sync_timestamp as synced.

    Records created after sync_timestamp remain pending.
    """

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE qr_invalid
            SET synced = 1
            WHERE synced = 0
              AND scan_ts <= ?
            """,
            (sync_timestamp,)
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

# ---------------------------------------------------------
# Full Local Refresh
# ---------------------------------------------------------

def local_full_refresh_qr_master(qr_records):
    """
    Completely refresh the local SQLite database from
    the cloud qr_master table.

    Refresh behavior
    ----------------
    1. Delete all local qr_transaction records.
    2. Delete all local qr_invalid records.
    3. Delete all local qr_master records.
    4. Bulk insert the complete cloud qr_master dataset.
    5. Mark all refreshed qr_master records as cloud_synced = 1.

    The entire operation is performed inside one SQLite
    transaction. If anything fails, the complete operation
    is rolled back.

    Parameters
    ----------
    qr_records : list[dict]
        Complete qr_master dataset retrieved from Supabase.

    Returns
    -------
    success : bool
    message : str
    """

    conn = get_connection()

    try:

        cursor = conn.cursor()

        # -------------------------------------------------
        # Start transaction
        # -------------------------------------------------

        conn.execute("BEGIN")

        # -------------------------------------------------
        # Wipe local transaction history
        # -------------------------------------------------

        cursor.execute(
            """
            DELETE FROM qr_transaction
            """
        )

        transaction_count = cursor.rowcount

        # -------------------------------------------------
        # Wipe local invalid QR history
        # -------------------------------------------------

        cursor.execute(
            """
            DELETE FROM qr_invalid
            """
        )

        invalid_count = cursor.rowcount

        # -------------------------------------------------
        # Wipe local QR master
        # -------------------------------------------------

        cursor.execute(
            """
            DELETE FROM qr_master
            """
        )

        master_deleted_count = cursor.rowcount

        # -------------------------------------------------
        # Prepare bulk QR master records
        # -------------------------------------------------

        values = []

        for qr in qr_records:

            values.append(
                (
                    qr["qr_code"],
                    qr.get("cycle_count", 0),
                    qr.get("qr_printed_ts"),
                    int(bool(qr.get("flagged", False))),
                    qr.get("flag_reason"),
                    qr.get("flag_mode"),
                    qr.get("flag_device_id"),
                    qr.get("flagged_ts"),
                    int(bool(qr.get("active_status", True))),
                    qr.get("discard_user"),
                    qr.get("discard_device_id"),
                    qr.get("discard_reason"),
                    qr.get("discard_ts"),
                    qr["created_ts"],
                    qr["updated_ts"],
                    qr["updated_by"],
                    1,
                    qr.get("qr_code_encoded")
                )
            )

        # -------------------------------------------------
        # Bulk insert QR master
        # -------------------------------------------------

        if values:

            cursor.executemany(
                """
                INSERT INTO qr_master
                (
                    qr_code,
                    cycle_count,
                    qr_printed_ts,
                    flagged,
                    flag_reason,
                    flag_mode,
                    flag_device_id,
                    flagged_ts,
                    active_status,
                    discard_user,
                    discard_device_id,
                    discard_reason,
                    discard_ts,
                    created_ts,
                    updated_ts,
                    updated_by,
                    cloud_synced,
                    qr_code_encoded
                )
                VALUES
                (
                    ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                values
            )

        # -------------------------------------------------
        # Commit complete refresh
        # -------------------------------------------------

        conn.commit()

        return (
            True,
            (
                "Local refresh completed successfully. "
                f"qr_master loaded: {len(values)}, "
                f"qr_master deleted: {master_deleted_count}, "
                f"transactions wiped: {transaction_count}, "
                f"invalid QR wiped: {invalid_count}."
            )
        )

    except Exception as ex:

        # -------------------------------------------------
        # Rollback everything
        # -------------------------------------------------

        conn.rollback()

        return (
            False,
            f"Local refresh failed: {ex}"
        )
    except Exception as ex:

        conn.rollback()

        return (
            False,
            str(ex)
        )
        
        
        
# ---------------------------------------------------------
# Get Pending Upload Counts
# ---------------------------------------------------------

def local_get_pending_upload_counts():
    """
    Return counts of local records waiting for cloud upload.

    Returns
    -------
    success : bool
    counts : dict | str

        {
            "qr_master": int,
            "transactions": int,
            "invalid": int,
            "total": int,
            "batch": int
        }

    batch = transactions + invalid

    qr_master is intentionally excluded from batch count.
    """

    try:

        conn = get_connection()

        cursor = conn.cursor()

        # -------------------------------------------------
        # QR Master
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM qr_master
            WHERE cloud_synced = 0
            """
        )

        qr_master_count = cursor.fetchone()[0]

        # -------------------------------------------------
        # Transactions
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM qr_transaction
            WHERE synced = 0
            """
        )

        transaction_count = cursor.fetchone()[0]

        # -------------------------------------------------
        # Invalid QR
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM qr_invalid
            WHERE synced = 0
            """
        )

        invalid_count = cursor.fetchone()[0]

        # -------------------------------------------------
        # Counts
        # -------------------------------------------------

        total_count = (
            qr_master_count
            + transaction_count
            + invalid_count
        )

        batch_count = (
            transaction_count
            + invalid_count
        )

        return (
            True,
            {
                "qr_master": qr_master_count,
                "transactions": transaction_count,
                "invalid": invalid_count,
                "total": total_count,
                "batch": batch_count
            }
        )

    except Exception as ex:

        return (
            False,
            str(ex)
        )
        
# ---------------------------------------------------------
# Incremental QR Master Refresh
# ---------------------------------------------------------

def local_incremental_refresh_qr_master(qr_records):
    """
    Insert or update qr_master records received from cloud.

    This is used for incremental cloud -> local
    synchronization.

    No local records are deleted.

    Parameters
    ----------
    qr_records : list[dict]
        QR master records retrieved from Supabase.

    Returns
    -------
    success : bool
    message : str
    """

    conn = get_connection()

    try:

        cursor = conn.cursor()

        # -------------------------------------------------
        # Start transaction
        # -------------------------------------------------

        conn.execute("BEGIN")

        inserted_count = 0
        updated_count = 0

        # -------------------------------------------------
        # Process QR master records
        # -------------------------------------------------

        for qr in qr_records:

            cursor.execute(
                """
                SELECT qr_code
                FROM qr_master
                WHERE qr_code = ?
                """,
                (qr["qr_code"],)
            )

            existing = cursor.fetchone()

            if existing is None:

                cursor.execute(
                    """
                    INSERT INTO qr_master
                    (
                        qr_code,
                        cycle_count,
                        qr_printed_ts,
                        flagged,
                        flag_reason,
                        flag_mode,
                        flag_device_id,
                        flagged_ts,
                        active_status,
                        discard_user,
                        discard_device_id,
                        discard_reason,
                        discard_ts,
                        created_ts,
                        updated_ts,
                        updated_by,
                        cloud_synced,
                        qr_code_encoded
                    )
                    VALUES
                    (
                        ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                    """,
                    (
                        qr["qr_code"],
                        qr.get("cycle_count", 0),
                        qr.get("qr_printed_ts"),
                        int(bool(qr.get("flagged", False))),
                        qr.get("flag_reason"),
                        qr.get("flag_mode"),
                        qr.get("flag_device_id"),
                        qr.get("flagged_ts"),
                        int(bool(qr.get("active_status", True))),
                        qr.get("discard_user"),
                        qr.get("discard_device_id"),
                        qr.get("discard_reason"),
                        qr.get("discard_ts"),
                        qr["created_ts"],
                        qr["updated_ts"],
                        qr["updated_by"],
                        1,
                        qr.get("qr_code_encoded")
                    )
                )

                inserted_count += 1

            else:

                cursor.execute(
                    """
                    UPDATE qr_master
                    SET
                        cycle_count = ?,
                        qr_printed_ts = ?,
                        flagged = ?,
                        flag_reason = ?,
                        flag_mode = ?,
                        flag_device_id = ?,
                        flagged_ts = ?,
                        active_status = ?,
                        discard_user = ?,
                        discard_device_id = ?,
                        discard_reason = ?,
                        discard_ts = ?,
                        created_ts = ?,
                        updated_ts = ?,
                        updated_by = ?,
                        cloud_synced = 1,
                        qr_code_encoded = ?
                    WHERE qr_code = ?
                    """,
                    (
                        qr.get("cycle_count", 0),
                        qr.get("qr_printed_ts"),
                        int(bool(qr.get("flagged", False))),
                        qr.get("flag_reason"),
                        qr.get("flag_mode"),
                        qr.get("flag_device_id"),
                        qr.get("flagged_ts"),
                        int(bool(qr.get("active_status", True))),
                        qr.get("discard_user"),
                        qr.get("discard_device_id"),
                        qr.get("discard_reason"),
                        qr.get("discard_ts"),
                        qr["created_ts"],
                        qr["updated_ts"],
                        qr["updated_by"],
                        qr.get("qr_code_encoded"),
                        qr["qr_code"]
                    )
                )

                updated_count += 1

        # -------------------------------------------------
        # Commit
        # -------------------------------------------------

        conn.commit()

        return (
            True,
            (
                "Incremental qr_master refresh completed. "
                f"Inserted: {inserted_count}, "
                f"Updated: {updated_count}."
            )
        )

    except Exception as ex:

        conn.rollback()

        return (
            False,
            f"Incremental qr_master refresh failed: {ex}"
        )