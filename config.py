"""
config.py
Central configuration file for the QR Scanner application.
"""

import os

# ==========================================================
# Project Paths
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Create folders if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "qr_database.db")
LOG_FILE = os.path.join(LOG_DIR, "qr_scanner.log")

# ==========================================================
# Device Information
# ==========================================================

DEVICE_ID = "PI001"

# ==========================================================
# Camera Configuration
# ==========================================================

CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_FPS = 30

# ==========================================================
# QR Scanner Configuration
# ==========================================================

SCAN_COOLDOWN_SECONDS = 2
MAX_QR_LENGTH = 100

# ==========================================================
# Relay Configuration
# ==========================================================

RELAY_ENABLED = True
RELAY_GPIO_PIN = 18
RELAY_ACTIVE_DURATION = 0.5      # seconds

# ==========================================================
# LED / Buzzer (Future)
# ==========================================================

LED_ENABLED = False
BUZZER_ENABLED = False

# ==========================================================
# Logging
# ==========================================================

LOG_LEVEL = "INFO"

# ==========================================================
# Synchronization
# ==========================================================

SYNC_INTERVAL_SECONDS = 300       # Every 5 minutes
HEARTBEAT_INTERVAL_SECONDS = 60

# ==========================================================
# Supabase Configuration
# ==========================================================

SUPABASE_URL = "https://fktjapjrbqphzwfndhdi.supabase.co"
SUPABASE_KEY = "sb_secret_Ao_Wr3H1k-kxZ7rWe5ft-w_RkKleI3e"

# ==========================================================
# Global Settings (Downloaded from Supabase)
# ==========================================================

GLOBAL_MAX_CYCLE = 30

# ==========================================================
# Database Table Names
# ==========================================================

TABLE_QR_MASTER = "qr_master"
TABLE_QR_INVALID = "qr_invalid"

# ==========================================================
# Status Values
# ==========================================================

STATUS_ACTIVE = "active"
STATUS_INACTIVE = "inactive"

# ==========================================================
# Validation Results
# ==========================================================

RESULT_VALID = "VALID"
RESULT_INVALID = "INVALID"
RESULT_NOT_FOUND = "NOT_FOUND"
RESULT_INACTIVE = "INACTIVE"
RESULT_MAX_CYCLE_EXCEEDED = "MAX_CYCLE_EXCEEDED"

# ==========================================================
# Application Information
# ==========================================================

APP_NAME = "QR Scanner"
APP_VERSION = "1.0.0"

####################################################
# Runtime Configuration
####################################################

APP_CONFIG = {}
