"""
health.py

Performs Supabase connectivity validation.

Author : Saravanakumar MJ
Project : QR Scanner
"""

from cloud.connection import get_client


def check_supabase():
    """
    Verifies Supabase connectivity.

    Returns
    -------
    (bool, str)
    """

    try:

        client = get_client()

        # Lightweight query
        client.table("qr_master") \
              .select("*") \
              .limit(1) \
              .execute()

        return (
            True,
            "Supabase connection successful."
        )

    except Exception as ex:

        return (
            False,
            str(ex)
        )