from fastapi import FastAPI
from app.routes import payments, people, accounts, summaries

app = FastAPI(title="Camiana Budget API")

app.include_router(payments.router)
# app.include_router(people.router)
# app.include_router(accounts.router)
app.include_router(summaries.router)


@app.get("/")
def root():
    return {"message": "Backend is running"}