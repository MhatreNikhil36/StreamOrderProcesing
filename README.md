# faststream-order-processor

A pair of services demonstrating FastStream’s Kafka integration:

1. **Order Gateway** (FastAPI) — accepts HTTP POSTs and enqueues to `orders`.  
2. **Order Processor** (FastStream) — consumes from `orders`, retries up to 3×, then forwards failures to `orders.DLQ`.

---

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.11+

### Quickstart

```bash
git clone https://github.com/your-org/faststream-order-processor.git
cd faststream-order-processor

# Bring up Zookeeper, Kafka, producer & consumer
docker compose up --build
````

* Order Gateway on `http://localhost:8001/orders`
* Processor binds to Kafka topic `orders`

You can POST JSON orders like:

```json
{
  "id": 123,
  "user": 42,
  "item": "widget",
  "qty": 2
}
```

---

## 📦 Project Structure

```text
.
├── producer
│   └── main.py         # FastAPI + Kafka publish
├── consumer
│   └── main.py         # FastStream subscriber + DLQ logic
├── docker-compose.yml
└── README.md
```

---

## 🛠 Future Roadmap

* [ ] **Schema Registry** – tighten payload contracts with Avro/Protobuf
* [ ] **Automated DLQ Handler** – spin off a service to reprocess or alert on DLQ messages
* [ ] **Monitoring & Metrics** – integrate Prometheus + Grafana dashboards
* [ ] **Graceful Shutdown** – ensure in-flight messages are drained on SIGTERM
* [ ] **Authentication** – secure HTTP API endpoints with OAuth2/JWT
* [ ] **Multi-Topic Processing** – add support for other event streams (e.g. `shipments`)

---

## 📄 License

MIT © NIkhil Mhatre
