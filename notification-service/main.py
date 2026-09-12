from fastapi import FastAPI, status
from pydantic import BaseModel
from typing import Dict

app = FastAPI(
    title="Notification Service",
    description="Internal notification delivery service for VulnerableMart",
    version="1.0.0"
)


class NotifyRequest(BaseModel):
    email: str
    message: str


class NotifyResponse(BaseModel):
    delivered: bool


@app.get("/healthz", status_code=status.HTTP_200_OK)
def health_check() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/notify", response_model=NotifyResponse, status_code=status.HTTP_200_OK)
def send_notification(notification: NotifyRequest):
    return NotifyResponse(delivered=True)
