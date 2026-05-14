from fastapi import APIRouter
from app.services import accounts
from app.models import account_models
from app.domain.account import AccountData
from app import errors

router = APIRouter()


@router.get("/accounts")
def get_accounts():
    return accounts.get_all_accounts()


@router.get("/accounts/{account_id}")
def get_account(account_id: int):
    account = accounts.get_account_by_id(account_id)

    if account is None:
        errors.raise_http_error(errors.ACCOUNT_NOT_FOUND)

    return account

@router.get("/people/{person_id}/accounts")
def get_accounts_for_person(person_id: int):

    result = accounts.get_accounts_by_person_id(person_id)

    if result["status"] == "error":
        errors.raise_result_error(result)

    return result

@router.get("/people/{person_id}/accounts/total")
def get_total_balance_for_person(person_id: int):
    result = accounts.get_total_balance_by_person_id(person_id)

    if result["status"] == "error":
        errors.raise_result_error(result)

    return result

@router.post("/accounts")
def add_account(data: account_models.AddAccountRequest):
    account = AccountData(**data.model_dump())
    result = accounts.create_account(account)

    if result["status"] == "error":
        errors.raise_result_error(result)

    return result

@router.put("/accounts/{account_id}")
def update_account(account_id: int, data: account_models.UpdateAccountRequest):
    account = AccountData(**data.model_dump())
    result = accounts.update_account(account_id, account)

    if result["status"] == "error":
        errors.raise_result_error(result)

    return result


@router.delete("/accounts/{account_id}")
def delete_account(account_id: int):
    result = accounts.delete_account(account_id)

    if result["status"] == "error":
        errors.raise_result_error(result)

    return result
