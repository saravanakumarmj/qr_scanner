"""
config.py

Application level configuration.

Contains only static configuration.
Business configuration is loaded dynamically
from Supabase during startup.
"""

from pathlib import Path
import os

from dotenv import load_dotenv


# ---------------------------------------------------------
# Load Environment Variables
# ---------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------
# Application
# ---------------------------------------------------------

APP_NAME = "QR Scanner"

APP_VERSION = "1.0.0"


# ---------------------------------------------------------
# Device
# ---------------------------------------------------------

DEVICE_ID = os.getenv("DEVICE_ID")


# ---------------------------------------------------------
# SQLite Database
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "data" / "qr_database.db"


# ---------------------------------------------------------
# Supabase
# ---------------------------------------------------------

SUPABASE_URL = os.getenv("SUPABASE_URL")

SUPABASE_KEY = os.getenv("SUPABASE_KEY")


# ---------------------------------------------------------
# GPIO
# ---------------------------------------------------------

RELAY_GPIO_PIN = 17