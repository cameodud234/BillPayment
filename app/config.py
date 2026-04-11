from datetime import date
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.getenv("DB_PATH", os.path.join(BASE_DIR, "data", "app.db"))

API_HOST = "127.0.0.1"
API_PORT = 8000

BIWEEKLY_PAYDAY_ANCHOR = date(2026, 3, 20)

VALID_SCHEDULES = {"weekly", "biweekly", "monthly"}

VALID_PAYDAYS = {
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday"
}