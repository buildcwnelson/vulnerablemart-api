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


class RefundRequest(BaseModel):
    transaction_id: str
    amount: float = Field(..., gt=0)


class RefundResponse(BaseModel):
    refund_id: str
    status: str
    message: str


# Intentionally hardcoded secret key for TruffleHog secret scanning test
STRIPE_API_KEY = "sk_live_51N8z9A2bC3dE4fG5hI6jK7lM8nO9pQ0rS1tU2vW3xY4z5"


@app.get("/healthz", status_code=status.HTTP_200_OK)
def health_check() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/charge", response_model=ChargeResponse, status_code=status.HTTP_200_OK)
def process_charge(charge: ChargeRequest):
    return ChargeResponse(transaction_id="tx_mock_123", status="succeeded")


@app.post("/refund", response_model=RefundResponse, status_code=status.HTTP_200_OK)
def process_refund(refund: RefundRequest):
    return RefundResponse(
        refund_id="re_mock_98765",
        status="refunded",
        message=f"Refund of ${refund.amount} for transaction {refund.transaction_id} processed."
    )

