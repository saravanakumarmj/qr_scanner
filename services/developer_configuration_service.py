"""
developer_configuration_service.py

Loads developer configuration for the QR Scanner application.

Author : Saravanakumar MJ
Project : QR Scanner
"""

from cloud.developer_configuration import (
    cloud_get_developer_configuration
)


class DeveloperConfiguration:

    developer_config_version = None
    background_check_interval_secs = None
    sync_cloud_to_local_interval_secs = None
    cache_cleanup_interval_secs = None
    upload_scheduler_check_interval_secs = None


def load_developer_configuration(developer_config_version):
    """
    Load developer configuration for the requested version.
    """

    success, config, message = cloud_get_developer_configuration(
        developer_config_version
    )

    if not success:
        return False, message

    DeveloperConfiguration.developer_config_version = config[
        "developer_config_version"
    ]

    DeveloperConfiguration.background_check_interval_secs = config[
        "background_check_interval_secs"
    ]

    DeveloperConfiguration.sync_cloud_to_local_interval_secs = config[
        "sync_cloud_to_local_interval_secs"
    ]

    DeveloperConfiguration.cache_cleanup_interval_secs = config[
        "cache_cleanup_interval_secs"
    ]

    DeveloperConfiguration.upload_scheduler_check_interval_secs = config[
        "upload_scheduler_check_interval_secs"
    ]

    return True, "Developer configuration loaded successfully."


def print_developer_configuration():

    print("")
    print("Developer Configuration")
    print("----------------------------------------")
    print(
        f"Developer Config Version        : "
        f"{DeveloperConfiguration.developer_config_version}"
    )
    print(
        f"Background Check Interval (Sec) : "
        f"{DeveloperConfiguration.background_check_interval_secs}"
    )
    print(
        f"Cloud -> Local Interval (Sec)   : "
        f"{DeveloperConfiguration.sync_cloud_to_local_interval_secs}"
    )
    print(
        f"Cache Cleanup Interval (Sec)    : "
        f"{DeveloperConfiguration.cache_cleanup_interval_secs}"
    )
    print(
        f"Upload Scheduler Check (Sec)    : "
        f"{DeveloperConfiguration.upload_scheduler_check_interval_secs}"
    )
    print("----------------------------------------")