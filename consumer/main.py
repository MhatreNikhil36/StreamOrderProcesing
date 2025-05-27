"""Order-processor service (manual DLQ version).

Consumes the **orders** topic, retries each message 3 times, then
publishes the failed payload to **orders.DLQ**.
"""
import os, random, logging
from faststream.kafka import KafkaBroker
from faststream import FastStream, Logger
from pydantic import BaseModel, Field

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")

broker = KafkaBroker(KAFKA_BOOTSTRAP)
app = FastStream(broker)


class Order(BaseModel):
    id: int
    user: int
    item: str
    qty: int = Field(gt=0)


@broker.subscriber(
    "orders",
    group_id="order-processor",
    retry=3,                  # FastStream will call us up to 4 times total
)
async def process_order(order: Order, logger: Logger):
    """Validate & process one order."""
    try:
        logger.info("processing order %s (qty=%s)", order.id, order.qty)

        # ----- business logic demo -----
        if random.random() < 0.2:                      # ~20 % failure
            raise ValueError("simulated business failure")
        # --------------------------------
        logger.info("✓ order %s processed", order.id)

    except Exception as exc:
        # Last try?  →  push to DLQ
        if order.__context__.retry_state.attempt >= order.__context__.max_retries:
            logger.warning("✗ final failure, sending %s to DLQ (%s)", order.id, exc)

            await broker.publish(
                order.model_dump(),        # raw JSON payload
                topic="orders.DLQ",
                key=str(order.user),        # whatever partition key you prefer
            )

        # re-raise so FastStream’s back-off / metrics still work
        raise
