"""
refresh_local_service.py

Performs a complete cloud -> local SQLite refresh.

Refresh Sequence
----------------
1. Fetch complete qr_master from Supabase.
2. Wipe local qr_transaction.
3. Wipe local qr_invalid.
4. Wipe local qr_master.
5. Bulk reload qr_master.
6. Mark all refreshed qr_master records as cloud_synced = 1.
"""

from cloud.repository import cloud_get_all_qr_master
from database.repository import local_full_refresh_qr_master


class RefreshLocalService:

    def run(self):
        """
        Execute a complete local SQLite refresh.

        Returns
        -------
        success : bool
        message : str
        """

        # -------------------------------------------------
        # Fetch complete cloud QR master
        # -------------------------------------------------

        success, qr_records = cloud_get_all_qr_master()

        if not success:

            return (
                False,
                f"Failed to fetch cloud qr_master: {qr_records}"
            )

        # -------------------------------------------------
        # Replace local database
        # -------------------------------------------------

        success, message = local_full_refresh_qr_master(
            qr_records
        )

        if not success:

            return (
                False,
                message
            )

        return (
            True,
            message
        )