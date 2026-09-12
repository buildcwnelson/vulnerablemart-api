from fastapi import FastAPI, status
from pydantic import BaseModel, Field
from typing import Dict

app = FastAPI(
    title="Payment Service",
    description="Internal payment processing service for VulnerableMart",
    version="1.0.0"
)


class ChargeRequest(BaseModel):
    amount: float = Field(..., gt=0)
    currency: str = Field(default="USD")


class ChargeResponse(BaseModel):
    transaction_id: str
    status: str


@app.get("/healthz", status_code=status.HTTP_200_OK)
def health_check() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/charge", response_model=ChargeResponse, status_code=status.HTTP_200_OK)
def process_charge(charge: ChargeRequest):
    return ChargeResponse(transaction_id="tx_mock_123", status="succeeded")
