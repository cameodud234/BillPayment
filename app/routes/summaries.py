from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from tinydb import TinyDB
from datetime import datetime, timedelta, date
from app.config import DB_PATH
from app.services import dashboard

router = APIRouter()

@router.get("/summaries/next-payday")
def next_payday_summary(today: str | None = None):
    return dashboard.get_next_payday_summary(today)