from fastapi import APIRouter
from app.services import accounts
from app.models import account_models

router = APIRouter()

@router.get("/accounts")
def get_accounts():
    return accounts.get_all_accounts()


@router.post("/accounts")
def add_account(data: account_models.AddAccountRequest):
    return accounts.create_account(data)