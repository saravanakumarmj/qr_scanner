"""
developer_configuration.py

Downloads developer configuration from Supabase.

Author : Saravanakumar MJ
Project : QR Scanner
"""

from cloud.connection import get_client


def cloud_get_developer_configuration(developer_config_version):
    """
    Downloads the developer configuration for the requested version.

    Parameters
    ----------
    developer_config_version : int
        Developer configuration version selected by the local app settings.

    Returns
    -------
    (success, config, message)
    """

    try:

        client = get_client()

        response = (
            client.table("app_developer_config")
            .select("*")
            .eq(
                "developer_config_version",
                developer_config_version
            )
            .limit(1)
            .execute()
        )

        if len(response.data) == 0:
            return (
                False,
                None,
                f"Developer configuration version "
                f"{developer_config_version} not found."
            )

        config = response.data[0]

        return (
            True,
            config,
            "Developer configuration downloaded successfully."
        )

    except Exception as ex:

        return (
            False,
            None,
            str(ex)
        )