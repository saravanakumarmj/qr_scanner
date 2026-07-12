"""
configuration.py

Downloads application configuration from Supabase.

Author : Saravanakumar MJ
Project : QR Scanner
"""

from cloud.connection import get_client


def get_configuration():
    """
    Downloads the active application configuration.

    Returns
    -------
    (success, config, message)
    """

    try:

        client = get_client()

        response = (
            client.table("app_configuration")
            .select("*")
            .eq("active", True)
            .limit(1)
            .execute()
        )

        if len(response.data) == 0:
            return (
                False,
                None,
                "No active configuration found."
            )

        config = response.data[0]

        return (
            True,
            config,
            "Configuration downloaded successfully."
        )

    except Exception as ex:

        return (
            False,
            None,
            str(ex)
        )