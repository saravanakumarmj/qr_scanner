"""
repository.py

Repository layer for all SQLite operations.
No SQL should exist outside this file.
"""

from datetime import datetime

from config import (
    TABLE_QR_MASTER,
    TABLE_QR_INVALID
)

from database.database import get_connection


class Repository:

    def __init__(self):
        self.conn = get_connection()

    # ---------------------------------------------------------
    # QR MASTER
    # ---------------------------------------------------------

    def get_qr(self, qr_code):
        """
        Returns one QR record or None.
        """

        cursor = self.conn.cursor()

        cursor.execute(
            f"""
            SELECT *
            FROM {TABLE_QR_MASTER}
            WHERE qr_code = ?
            """,
            (qr_code,)
        )

        return cursor.fetchone()

    # ---------------------------------------------------------

    def increment_cycle(self, qr_code):
        """
        Increment cycle count by 1
        """

        cursor = self.conn.cursor()

        cursor.execute(
            f"""
            UPDATE {TABLE_QR_MASTER}
            SET cycle_count = cycle_count + 1
            WHERE qr_code = ?
            """,
            (qr_code,)
        )

        self.conn.commit()

        return cursor.rowcount

    # ---------------------------------------------------------

    def update_last_scan(self, qr_code):

        cursor = self.conn.cursor()

        cursor.execute(
            f"""
            UPDATE {TABLE_QR_MASTER}
            SET last_scan = ?
            WHERE qr_code = ?
            """,
            (
                datetime.now().isoformat(),
                qr_code
            )
        )

        self.conn.commit()

        return cursor.rowcount

    # ---------------------------------------------------------

    def update_cycle_and_last_scan(self, qr_code):

        cursor = self.conn.cursor()

        cursor.execute(
            f"""
            UPDATE {TABLE_QR_MASTER}
            SET
                cycle_count = cycle_count + 1,
                last_scan = ?
            WHERE qr_code = ?
            """,
            (
                datetime.now().isoformat(),
                qr_code
            )
        )

        self.conn.commit()

        return cursor.rowcount

    # ---------------------------------------------------------
    # INVALID QR
    # ---------------------------------------------------------

    def insert_invalid_scan(
            self,
            raw_code,
            device_id,
            resolved=False
    ):

        cursor = self.conn.cursor()

        cursor.execute(
            f"""
            INSERT INTO {TABLE_QR_INVALID}
            (
                raw_code,
                device_id,
                scan_ts,
                resolved
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                raw_code,
                device_id,
                datetime.now().isoformat(),
                resolved
            )
        )

        self.conn.commit()

        return cursor.lastrowid
