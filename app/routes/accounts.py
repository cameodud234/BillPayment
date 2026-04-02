from fastapi import APIRouter
from pydantic import BaseModel
from app.services import accounts

router = APIRouter()


class AddAccountRequest(BaseModel):
    person_id: int | None = None
    name: str
    type: str
    balance: float
    updated_at: str | None = None


@router.get("/accounts")
def get_accounts():
    return accounts.get_all_accounts()


@router.post("/accounts")
def add_account(data: AddAccountRequest):
    return accounts.create_account(
        person_id=data.person_id,
        name=data.name,
        account_type=data.type,
        balance=data.balance,
        updated_at=data.updated_at
    )