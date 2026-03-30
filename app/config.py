# app/config.py

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(BASE_DIR, "data", "bills.json")

API_HOST = "127.0.0.1"
API_PORT = 8000

WIFE_PAYDAY_ANCHOR = "2026-03-20"