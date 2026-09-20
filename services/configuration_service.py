"""
configuration_service.py

Loads the active application configuration
from Supabase.

The configuration is cached in memory and
used by the entire application.
"""

#from cloud.repository import cloud_get_active_configuration
from cloud.configuration import cloud_get_configuration

# ---------------------------------------------------------
# Configuration Cache
# ---------------------------------------------------------

class Configuration:

    # Business Rules
    max_cycle = None
    max_age_days = None

    # Upload Configuration
    upload_mode = None

    upload_interval_secs = None

    upload_batch_size = None

    # Device Configuration
    relay_on_time = None

    heartbeat_interval = None

    scanner_timeout = None

    app_version = None


# ---------------------------------------------------------
# Load Configuration
# ---------------------------------------------------------

def load_configuration():
    """
    Loads the active configuration from Supabase.

    Returns
    -------
    success : bool

    message : str
    """

    success, config, message = cloud_get_configuration()

    if not success:

        return (
            False,
            message
        )

# Config data for flagging
    Configuration.max_cycle = config["max_cycle"]
    Configuration.max_age_days = config["max_age_days"]

# Config data for local -> cloud sync
    Configuration.upload_mode = config["upload_mode"]
    Configuration.upload_interval_secs = config["upload_interval_secs"]
    Configuration.upload_batch_size = config["upload_batch_size"]


    Configuration.relay_on_time = config["relay_on_time"]
    Configuration.heartbeat_interval = config["heartbeat_interval"]
    Configuration.scanner_timeout = config["scanner_timeout"]

    Configuration.app_version = config["app_version"]


    return (
        True,
        "Configuration loaded successfully."
    )


# ---------------------------------------------------------
# Print Configuration
# ---------------------------------------------------------

def print_configuration():
    """
    Prints the currently loaded configuration.
    """

    print()

    print("Application Configuration")

    print("---------------------------------------")

    print(f"Max Cycle              : {Configuration.max_cycle}")


    print(f"Max Age Days           : {Configuration.max_age_days}")


    print(f"Upload Mode            : {Configuration.upload_mode}")

    print(f"Upload Interval (Sec)  : {Configuration.upload_interval_secs}")

    print(f"Upload Batch Size      : {Configuration.upload_batch_size}")


    print(f"Relay ON Time          : {Configuration.relay_on_time}")

    print(f"Heartbeat Interval     : {Configuration.heartbeat_interval}")

    print(f"Scanner Timeout        : {Configuration.scanner_timeout}")

    print(f"App Version            : {Configuration.app_version}")

    print("---------------------------------------")

    print()