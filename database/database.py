"""
database.py

SQLite Connection Manager

Responsibilities:
- Maintain a single shared SQLite connection
- Enable Foreign Keys
- Commit / Rollback Transactions
- Close connection gracefully
"""

import sqlite3
import threading

from config import DB_PATH

# --------------------------------------------------
# Global Connection Object
# --------------------------------------------------

_connection = None
_lock = threading.Lock()


# --------------------------------------------------
# Connect to SQLite
# --------------------------------------------------

def connect():
    """
    Opens the SQLite database connection only once.
    """

    global _connection

    with _lock:

        if _connection is None:

            _connection = sqlite3.connect(
                DB_PATH,
                check_same_thread=False
            )

            # Return rows as dictionary-like objects
            _connection.row_factory = sqlite3.Row

            # Enable Foreign Keys
            _connection.execute("PRAGMA foreign_keys = ON;")

    return _connection


# --------------------------------------------------
# Get Existing Connection
# --------------------------------------------------

def get_connection():

    global _connection

    if _connection is None:
        return connect()

    return _connection


# --------------------------------------------------
# Commit Transaction
# --------------------------------------------------

def commit():

    conn = get_connection()
    conn.commit()


# --------------------------------------------------
# Rollback Transaction
# --------------------------------------------------

def rollback():

    conn = get_connection()
    conn.rollback()


# --------------------------------------------------
# Close Database
# --------------------------------------------------

def close():

    global _connection

    if _connection is not None:
        _connection.close()
        _connection = None


# --------------------------------------------------
# Check Connection Status
# --------------------------------------------------

def is_connected():

    return _connection is not None
