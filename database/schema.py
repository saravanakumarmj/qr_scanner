"""
schema.py

Initializes the SQLite database by executing all SQL scripts
found in the database/sql directory.

The SQL files are executed in filename order.

Example:
01_qr_master.sql
02_qr_device.sql
03_qr_error_code.sql
...
"""

import os

from database.database import get_connection


def initialize_database():

    conn = get_connection()

    cursor = conn.cursor()

    sql_folder = os.path.join(
        os.path.dirname(__file__),
        "sql"
    )

    sql_files = sorted(
        [
            file
            for file in os.listdir(sql_folder)
            if file.endswith(".sql")
        ]
    )

    print("\nInitializing database...\n")

    for file_name in sql_files:

        file_path = os.path.join(sql_folder, file_name)

        print(f"Executing : {file_name}")

        with open(file_path, "r", encoding="utf-8") as sql_file:

            sql_script = sql_file.read()

            cursor.executescript(sql_script)

    conn.commit()

    print("\nDatabase initialized successfully.\n")
