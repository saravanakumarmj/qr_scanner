"""
database/health.py

Database health checks.
"""

import sqlite3

from config import DB_PATH


REQUIRED_TABLES = [
    "qr_master",
    "qr_transaction",
    "qr_invalid",
    "qr_error_code",
    "qr_device",
    "sync_state"
]


def check_database():

    try:

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check database connectivity
        cursor.execute("SELECT 1")

        # Get all tables
        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table'
        """)

        tables = {row[0] for row in cursor.fetchall()}

        # Verify required tables
        missing_tables = []

        for table in REQUIRED_TABLES:
            if table not in tables:
                missing_tables.append(table)

        conn.close()

        if missing_tables:

            return (
                False,
                f"Missing tables : {', '.join(missing_tables)}"
            )

        return (
            True,
            "Database health check successful."
        )

    except Exception as ex:

        return (
            False,
            str(ex)
        )
