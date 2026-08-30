"""
test_upload_sync.py

Manual integration test for the local -> Supabase synchronization.

This test:
1. Captures one synchronization timestamp.
2. Runs the real UploadService.
3. Displays the result.
4. Shows remaining pending records in SQLite.

It does NOT create test records.
"""

from datetime import datetime

from database.repository import (
    local_get_pending_transactions,
    local_get_pending_invalid,
    local_get_modified_qr_master,
)

from services.upload_service import UploadService


def get_pending_counts(sync_timestamp):
    """
    Get the number of records that belong to the
    current synchronization window.
    """

    success, transactions = local_get_pending_transactions(
        sync_timestamp
    )

    if not success:
        return False, transactions

    success, invalid = local_get_pending_invalid(
        sync_timestamp
    )

    if not success:
        return False, invalid

    success, qr_master = local_get_modified_qr_master(
        sync_timestamp
    )

    if not success:
        return False, qr_master

    return (
        True,
        {
            "transactions": len(transactions),
            "invalid": len(invalid),
            "qr_master": len(qr_master),
        }
    )


def get_remaining_pending():
    """
    Get the current number of unsynchronized records,
    regardless of timestamp.
    """

    success, transactions = local_get_pending_transactions(
        "9999-12-31 23:59:59"
    )

    if not success:
        return False, transactions

    success, invalid = local_get_pending_invalid(
        "9999-12-31 23:59:59"
    )

    if not success:
        return False, invalid

    success, qr_master = local_get_modified_qr_master(
        "9999-12-31 23:59:59"
    )

    if not success:
        return False, qr_master

    return (
        True,
        {
            "transactions": len(transactions),
            "invalid": len(invalid),
            "qr_master": len(qr_master),
        }
    )


def main():
    """
    Run the synchronization integration test.
    """

    print()
    print("=" * 60)
    print("LOCAL -> CLOUD SYNC TEST")
    print("=" * 60)

    # -----------------------------------------------------
    # Capture synchronization timestamp
    # -----------------------------------------------------

    sync_timestamp = datetime.now().isoformat(
        sep=" ",
        timespec="seconds"
    )

    print()
    print("Sync Timestamp")
    print("----------------")
    print(sync_timestamp)

    # -----------------------------------------------------
    # Check records included in this sync
    # -----------------------------------------------------

    success, counts = get_pending_counts(
        sync_timestamp
    )

    if not success:

        print()
        print("ERROR:")
        print(counts)
        return

    print()
    print("Records in Sync Window")
    print("-----------------------")
    print(
        f"Transactions : {counts['transactions']}"
    )
    print(
        f"QR Master    : {counts['qr_master']}"
    )
    print(
        f"Invalid QR   : {counts['invalid']}"
    )

    total = (
        counts["transactions"]
        + counts["qr_master"]
        + counts["invalid"]
    )

    print(
        f"Total        : {total}"
    )

    if total == 0:

        print()
        print("Nothing to synchronize.")
        return

    # -----------------------------------------------------
    # Run actual upload service
    # -----------------------------------------------------

    print()
    print("Starting upload...")
    print("-------------------")

    service = UploadService()

    success, message = service.run(
        sync_timestamp
    )

    print()
    print("Upload Result")
    print("-------------")
    print(f"Success : {success}")
    print(f"Message : {message}")

    # -----------------------------------------------------
    # Check remaining pending records
    # -----------------------------------------------------

    success, remaining = get_remaining_pending()

    if not success:

        print()
        print("ERROR checking remaining records:")
        print(remaining)
        return

    print()
    print("Remaining Pending Records")
    print("-------------------------")
    print(
        f"Transactions : {remaining['transactions']}"
    )
    print(
        f"QR Master    : {remaining['qr_master']}"
    )
    print(
        f"Invalid QR   : {remaining['invalid']}"
    )

    # -----------------------------------------------------
    # Final result
    # -----------------------------------------------------

    print()

    if success:

        print("=" * 60)
        print("SYNC TEST COMPLETED")
        print("=" * 60)

    print()


if __name__ == "__main__":
    main()