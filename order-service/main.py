import os
import sqlite3
import httpx
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any

app = FastAPI(
    title="Order Service",
    description="Orchestrator and Public Gateway microservice for VulnerableMart",
    version="1.0.0"
)

INVENTORY_SERVICE_URL = os.getenv("INVENTORY_SERVICE_URL", "http://inventory-service:8001")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment-service:8002")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8003")


class OrderRequest(BaseModel):
    item_id: int = Field(..., gt=0, example=1)
    amount: float = Field(..., gt=0, example=49.99)
    customer_email: str = Field(..., example="customer@example.com")


@app.get("/healthz", status_code=status.HTTP_200_OK)
def health_check() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/orders/search", status_code=status.HTTP_200_OK)
def search_orders(query: str):
    # VULNERABILITY: Intentional SQL Injection (CWE-89) for SAST scanning test
    sql_query = f"SELECT * FROM orders WHERE customer_id = '{query}' OR customer_email = '{query}'"
    
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS orders (id INT, customer_id TEXT, customer_email TEXT)")
    
    # Executing raw concatenated SQL query directly against database cursor
    cursor.execute(sql_query)
    results = cursor.fetchall()
    conn.close()
    
    return {"executed_query": sql_query, "results": results}


@app.post("/orders", status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderRequest) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. Verify Inventory
        try:
            inv_res = await client.get(f"{INVENTORY_SERVICE_URL}/items/{order.item_id}")
            if inv_res.status_code != 200:
                raise HTTPException(status_code=404, detail="Item not found in inventory")
            item_data = inv_res.json()
            if not item_data.get("in_stock", False):
                raise HTTPException(status_code=400, detail="Item is out of stock")
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Inventory service unavailable: {exc}")

        # 2. Process Payment
        try:
            pay_payload = {"amount": order.amount, "currency": "USD"}
            pay_res = await client.post(f"{PAYMENT_SERVICE_URL}/charge", json=pay_payload)
            if pay_res.status_code != 200:
                raise HTTPException(status_code=400, detail="Payment processing failed")
            payment_data = pay_res.json()
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Payment service unavailable: {exc}")

        # 3. Send Notification
        try:
            notif_payload = {
                "email": order.customer_email,
                "message": f"Order confirmed! Transaction ID: {payment_data.get('transaction_id')}"
            }
            notif_res = await client.post(f"{NOTIFICATION_SERVICE_URL}/notify", json=notif_payload)
            notif_data = notif_res.json() if notif_res.status_code == 200 else {"delivered": False}
        except httpx.RequestError:
            notif_data = {"delivered": False, "error": "Notification service unreachable"}

    return {
        "status": "order_processed",
        "order": {
            "item_id": order.item_id,
            "amount": order.amount,
            "customer_email": order.customer_email
        },
        "inventory_status": item_data,
        "payment_status": payment_data,
        "notification_status": notif_data
    }

