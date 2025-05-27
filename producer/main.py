
"""Order producer service.

Exposes an HTTP API (FastAPI) that accepts order JSON and publishes it to the
Kafka topic **orders** using FastStream's KafkaBroker.

Run locally:
    uvicorn main:app --reload --host 0.0.0.0 --port 8001
"""
import asyncio, os
from fastapi import FastAPI, HTTPException
from faststream.kafka import KafkaBroker
from pydantic import BaseModel, Field

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")

broker = KafkaBroker(KAFKA_BOOTSTRAP)
app = FastAPI(title="Order Gateway")

class Order(BaseModel):
    id: int
    user: int
    item: str
    qty: int = Field(gt=0, description="Quantity ordered (must be > 0)")

@app.on_event("startup")
async def _startup():
    for attempt in range(10):          # <= 10×1 s ~ 10 s grace
        try:
            await broker.start()
            break
        except Exception as exc:
            print(f"Kafka not ready ({exc}), retry {attempt+1}/10")
            await asyncio.sleep(1)

@app.on_event("shutdown")
async def _shutdown():
    await broker.close()

@app.post("/orders", status_code=202, summary="Queue a new order")
async def create_order(order: Order):
    """Publish the order to Kafka.
    We key by *user* so that orders by the same user stay on the same partition.
    """
    try:
        await broker.publish(
            order.model_dump(),
            topic="orders",
            key=str(order.user).encode("utf-8")  # encode to bytes for Kafka key
        )
        return {"status": "queued"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
