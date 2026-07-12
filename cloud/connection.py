"""
connection.py

Creates and returns a Supabase client.

Author : Saravanakumar MJ
Project : QR Scanner
"""

from supabase import create_client, Client

from config import (
    SUPABASE_URL,
    SUPABASE_KEY
)


_supabase_client = None


def get_client() -> Client:
    """
    Returns a singleton Supabase client.
    """

    global _supabase_client

    if _supabase_client is None:
        _supabase_client = create_client(
            SUPABASE_URL,
            SUPABASE_KEY
        )

    return _supabase_client