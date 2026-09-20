
"""
services/app_settings.py

Loads local application settings from app_settings.json.

These settings control local application behavior only.
They are separate from the business configuration loaded
from Supabase into config.APP_CONFIG and the developer
configuration loaded from Supabase.
"""

import json
from pathlib import Path


# ---------------------------------------------------------
# File Location
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_FILE = BASE_DIR / "app_settings.json"


# ---------------------------------------------------------
# Default Settings
# ---------------------------------------------------------

DEFAULT_SETTINGS = {
    "developer_config_version": 1,
    "populate_recent_cache": "YES"
}


# ---------------------------------------------------------
# Runtime Settings
# ---------------------------------------------------------

APP_SETTINGS = {}


# ---------------------------------------------------------
# Internal Warning Helper
# ---------------------------------------------------------

def _warning(message):
    print(f"[CONFIG] WARNING: {message}")


# ---------------------------------------------------------
# Load Settings
# ---------------------------------------------------------

def load_app_settings():
    """
    Load local application settings from app_settings.json.

    If the file or any setting is invalid/missing, the
    corresponding default value is used and a clear warning
    is printed.

    Returns
    -------
    success, message
    """

    APP_SETTINGS.clear()

    # Start with defaults.
    # Valid values from the file will overwrite these.
    APP_SETTINGS.update(DEFAULT_SETTINGS)

    # -----------------------------------------------------
    # Check File
    # -----------------------------------------------------

    if not SETTINGS_FILE.exists():

        _warning(
            f"Application settings file not found: "
            f"{SETTINGS_FILE}"
        )

        _warning(
            "All application settings are using default values."
        )

        return (
            False,
            "Application settings file not found. Using defaults."
        )

    # -----------------------------------------------------
    # Read JSON
    # -----------------------------------------------------

    try:

        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

    except json.JSONDecodeError as ex:

        _warning(
            f"Invalid JSON in {SETTINGS_FILE}."
        )

        _warning(
            f"JSON error at line {ex.lineno}, column {ex.colno}: "
            f"{ex.msg}"
        )

        _warning(
            "All application settings are using default values."
        )

        return (
            False,
            "Invalid application settings JSON. Using defaults."
        )

    except Exception as ex:

        _warning(
            f"Unable to read {SETTINGS_FILE}: {ex}"
        )

        _warning(
            "All application settings are using default values."
        )

        return (
            False,
            "Unable to read application settings. Using defaults."
        )

    # -----------------------------------------------------
    # Validate Root
    # -----------------------------------------------------

    if not isinstance(data, dict):

        _warning(
            "Application settings file must contain a JSON object."
        )

        _warning(
            "All application settings are using default values."
        )

        return (
            False,
            "Invalid application settings structure. Using defaults."
        )

    # -----------------------------------------------------
    # Validate Settings Section
    # -----------------------------------------------------

    settings = data.get("settings")

    if settings is None:

        _warning(
            "'settings' section is missing from app_settings.json."
        )

        _warning(
            "All application settings are using default values."
        )

        return (
            False,
            "Settings section missing. Using defaults."
        )

    if not isinstance(settings, dict):

        _warning(
            "'settings' section must be a JSON object."
        )

        _warning(
            "All application settings are using default values."
        )

        return (
            False,
            "Invalid settings section. Using defaults."
        )

    # -----------------------------------------------------
    # Load Individual Settings
    # -----------------------------------------------------

    warnings_found = False

    for key, default_value in DEFAULT_SETTINGS.items():

        if key not in settings:

            _warning(
                f"Setting '{key}' is missing. "
                f"Using default value: {default_value}"
            )

            warnings_found = True
            continue

        value = settings[key]

        # -------------------------------------------------
        # Developer Configuration Version
        # -------------------------------------------------

        if key == "developer_config_version":

            if (
                isinstance(value, bool)
                or not isinstance(value, int)
                or value <= 0
            ):

                _warning(
                    f"Setting '{key}' has invalid value: {value}. "
                    f"Using default value: {default_value}"
                )

                warnings_found = True
                continue

            APP_SETTINGS[key] = value

        # -------------------------------------------------
        # YES / NO Setting
        # -------------------------------------------------

        else:

            normalized_value = str(value).upper()

            if normalized_value not in ("YES", "NO"):

                _warning(
                    f"Setting '{key}' has invalid value: {value}. "
                    f"Expected YES or NO. "
                    f"Using default value: {default_value}"
                )

                warnings_found = True
                continue

            APP_SETTINGS[key] = normalized_value

    # -----------------------------------------------------
    # Result
    # -----------------------------------------------------

    if warnings_found:

        _warning(
            "One or more application settings had problems. "
            "Defaults were used where required."
        )

        return (
            False,
            "Application settings loaded with warnings."
        )

    print("[CONFIG] Application settings loaded successfully.")

    return (
        True,
        "Application settings loaded successfully."
    )


# ---------------------------------------------------------
# Get Setting
# ---------------------------------------------------------

def get_app_setting(key, default=None):
    """
    Returns a loaded application setting.

    Parameters
    ----------
    key : str
        Setting name.

    default : any
        Value returned if the setting is not available.
    """

    return APP_SETTINGS.get(key, default)


# ---------------------------------------------------------
# Print Settings
# ---------------------------------------------------------

def print_app_settings():

    print("[CONFIG] Local Application Settings")
    print("[CONFIG] ----------------------------------------")

    for key, value in APP_SETTINGS.items():

        print(
            f"[CONFIG] {key} = {value}"
        )

    print("[CONFIG] ----------------------------------------")
