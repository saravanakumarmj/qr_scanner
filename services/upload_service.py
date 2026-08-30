"""
upload_service.py

Uploads local SQLite changes to Supabase.

Upload Sequence
---------------
1. Capture sync_timestamp
2. Upload pending qr_transaction records up to sync_timestamp
3. Upload modified qr_master records up to sync_timestamp
4. Upload pending qr_invalid records up to sync_timestamp
5. Mark all successfully uploaded local records as synced
   using the same sync_timestamp

Important
---------
Records created/modified after sync_timestamp are NOT included
in this upload cycle. They remain pending for the next cycle.
"""

from database.repository import (
    local_get_pending_transactions,
    local_get_pending_invalid,
    local_get_modified_qr_master,
    local_mark_transactions_synced,
    local_mark_qr_master_synced,
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

    # ---------------------------------------------------------
    # Main Upload Process
    # ---------------------------------------------------------

    def run(self, sync_timestamp):
        """
        Executes one complete upload cycle.

        Parameters
        ----------
        sync_timestamp : str
            Timestamp defining the boundary of this upload cycle.

        Returns
        -------
        success : bool
        message : str
        """

        # -----------------------------------------------------
        # 1. Upload Transactions
        # -----------------------------------------------------

        success, message = self.upload_transactions(
            sync_timestamp
        )

        if not success:
            return False, message

        # -----------------------------------------------------
        # 2. Upload QR Master
        # -----------------------------------------------------

        success, message = self.upload_qr_master(
            sync_timestamp
        )

        if not success:
            return False, message

        # -----------------------------------------------------
        # 3. Upload Invalid QR
        # -----------------------------------------------------

        success, message = self.upload_invalid(
            sync_timestamp
        )

        if not success:
            return False, message

        # -----------------------------------------------------
        # 4. Mark Local Records as Synced
        # -----------------------------------------------------

        success, message = self.complete_upload(
            sync_timestamp
        )

        return success, message

    # ---------------------------------------------------------
    # Upload Transactions
    # ---------------------------------------------------------

    def upload_transactions(self, sync_timestamp):
        """
        Upload pending qr_transaction records whose scan timestamp
        is at or before the synchronization timestamp.
        """

        success, transactions = local_get_pending_transactions(
            sync_timestamp
        )

        if not success:
            return False, transactions

        self.pending_transactions = transactions

        if not transactions:

            return (
                True,
                "No pending transactions."
            )

        # -----------------------------------------------------
        # Upload to Supabase
        # -----------------------------------------------------

        success, message = cloud_insert_transactions(
            transactions
        )

        if not success:
            return False, message

        return (
            True,
            message
        )

    # ---------------------------------------------------------
    # Upload QR Master
    # ---------------------------------------------------------

    def upload_qr_master(self, sync_timestamp):
        """
        Upload qr_master records that were modified locally
        up to the synchronization timestamp.

        qr_code_encoded is intentionally not uploaded.
        """

        success, qr_records = local_get_modified_qr_master(
            sync_timestamp
        )

        if not success:
            return False, qr_records

        self.modified_qr = qr_records

        if not qr_records:

            return (
                True,
                "No qr_master updates."
            )

        # -----------------------------------------------------
        # Upload to Supabase
        # -----------------------------------------------------

        success, message = cloud_update_qr_master(
            qr_records
        )

        if not success:
            return False, message

        return (
            True,
            message
        )

    # ---------------------------------------------------------
    # Upload Invalid QR
    # ---------------------------------------------------------

    def upload_invalid(self, sync_timestamp):
        """
        Upload pending invalid QR records whose scan timestamp
        is at or before the synchronization timestamp.
        """

        success, invalid = local_get_pending_invalid(
            sync_timestamp
        )

        if not success:
            return False, invalid

        self.pending_invalid = invalid

        if not invalid:

            return (
                True,
                "No pending invalid QR records."
            )

        # -----------------------------------------------------
        # Upload to Supabase
        # -----------------------------------------------------

        success, message = cloud_insert_invalid_qr(
            invalid
        )

        if not success:
            return False, message

        return (
            True,
            message
        )

    # ---------------------------------------------------------
    # Complete Upload
    # ---------------------------------------------------------

    def complete_upload(self, sync_timestamp):
        """
        Marks all records belonging to this synchronization
        window as successfully synchronized.

        The same sync_timestamp used for selecting records is
        used here to prevent records created during the upload
        from being marked as synced.
        """

        # -----------------------------------------------------
        # Mark Transactions
        # -----------------------------------------------------

        success, message = local_mark_transactions_synced(
            sync_timestamp
        )

        if not success:
            return False, message

        # -----------------------------------------------------
        # Mark QR Master
        # -----------------------------------------------------

        success, message = local_mark_qr_master_synced(
            sync_timestamp
        )

        if not success:
            return False, message

        # -----------------------------------------------------
        # Mark Invalid QR
        # -----------------------------------------------------

        success, message = local_mark_invalid_synced(
            sync_timestamp
        )

        if not success:
            return False, message

        # -----------------------------------------------------
        # Completed
        # -----------------------------------------------------

        return (
            True,
            "Upload completed successfully."
        )