from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Dict

app = FastAPI(
    title="Inventory Service",
    description="Internal inventory service for VulnerableMart",
    version="1.0.0"
)


class ItemResponse(BaseModel):
    item_id: int
    in_stock: bool
    price: float


@app.get("/healthz", status_code=status.HTTP_200_OK)
def health_check() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/items/{item_id}", response_model=ItemResponse, status_code=status.HTTP_200_OK)
def get_item(item_id: int):
    if item_id <= 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemResponse(item_id=item_id, in_stock=True, price=49.99)
