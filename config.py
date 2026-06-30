# Database creidentials & SMTP credentials are stored in a separate file for security reasons. Please create a file named `config.py` in the same directory as this script and add the following variables:

"""
Central Configuration File
Intrusion Detection System
"""

import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# ==================================================
# DATABASE CONFIG
# ==================================================

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT", "5432")
}

# ==================================================
# EMAIL CONFIG
# ==================================================

EMAIL_CONFIG = {
    "sender_email": os.getenv("SENDER_EMAIL"),
    "receiver_email": os.getenv("RECEIVER_EMAIL"),
    "app_password": os.getenv("EMAIL_APP_PASSWORD"),
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587
}

# ==================================================
# AI SETTINGS
# ==================================================

CONFIDENCE_THRESHOLD = 0.50

# seconds
ALERT_COOLDOWN = 60

# ==================================================
# WEB SETTINGS
# ==================================================

BASE_URL = os.getenv(
    "BASE_URL",
    "http://127.0.0.1:5000"
)

# ==================================================
# SNAPSHOT STORAGE
# ==================================================

SNAPSHOT_DIR = "static/snapshots"

# ==================================================
# DEFAULT CAMERA
# ==================================================

DEFAULT_CAMERA_LOCATION = (
    "Warehouse Main Entrance"
)