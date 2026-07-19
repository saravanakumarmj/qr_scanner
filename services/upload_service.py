"""
upload_service.py

Uploads local SQLite changes to Supabase.

Upload Sequence
---------------
1. Upload qr_transaction
2. Update qr_master
3. Upload qr_invalid
4. Mark local records as synced
"""

from database.repository import (
    local_get_pending_transactions,
    local_get_pending_invalid,
    local_get_modified_qr_master,
    local_mark_transactions_synced,
    local_mark_invalid_synced
)

from cloud.repository import (
    cloud_insert_transactions,
    cloud_insert_invalid_qr,
    cloud_update_qr_master
)


class UploadService:

    def __init__(self):

        self.pending_transactions = []

        self.pending_invalid = []

        self.modified_qr = []

        self.transaction_ids = []

        self.invalid_ids = []

    # ---------------------------------------------------------
    # Main Upload Process
    # ---------------------------------------------------------

    def run(self):
        """
        Executes one upload cycle.
        """

        # Upload transactions
        success, message = self.upload_transactions()

        if not success:
            return success, message

        # Update qr_master
        success, message = self.upload_qr_master()

        if not success:
            return success, message

        # Upload invalid QR
        success, message = self.upload_invalid()

        if not success:
            return success, message

        # Mark local records as synced
        success, message = self.complete_upload()

        return success, message

    # ---------------------------------------------------------
    # Upload Transactions
    # ---------------------------------------------------------

    def upload_transactions(self):

        success, transactions = local_get_pending_transactions()

        if not success:
            return False, transactions

        if len(transactions) == 0:
            return True, "No pending transactions."

        self.pending_transactions = transactions

        self.transaction_ids = [
            row["transaction_id"]
            for row in transactions
        ]

        # Upload transaction records
        success, message = cloud_insert_transactions(
            transactions
        )

        if not success:
            return False, message

        # Earliest scan timestamp
        earliest_scan_ts = min(
            row["scan_ts"]
            for row in transactions
        )

        # Read modified qr_master records
        success, qr_records = local_get_modified_qr_master(
            earliest_scan_ts
        )

        if not success:
            return False, qr_records

        self.modified_qr = qr_records

        return True, message

    # ---------------------------------------------------------
    # Upload QR Master
    # ---------------------------------------------------------

    def upload_qr_master(self):

        if len(self.modified_qr) == 0:

            return (
                True,
                "No qr_master updates."
            )

        return cloud_update_qr_master(
            self.modified_qr
        )

    # ---------------------------------------------------------
    # Upload Invalid QR
    # ---------------------------------------------------------

    def upload_invalid(self):

        success, invalid = local_get_pending_invalid()

        if not success:
            return False, invalid

        if len(invalid) == 0:

            return (
                True,
                "No invalid QR records."
            )

        self.pending_invalid = invalid

        self.invalid_ids = [
            row["invalid_id"]
            for row in invalid
        ]

        return cloud_insert_invalid_qr(
            invalid
        )

    # ---------------------------------------------------------
    # Complete Upload
    # ---------------------------------------------------------

    def complete_upload(self):

        # Mark uploaded transactions as synced
        if self.transaction_ids:

            success, message = local_mark_transactions_synced(
                self.transaction_ids
            )

            if not success:
                return success, message

        # Mark uploaded invalid records as synced
        if self.invalid_ids:

            success, message = local_mark_invalid_synced(
                self.invalid_ids
            )

            if not success:
                return success, message

        return (
            True,
            "Upload completed successfully."
        )