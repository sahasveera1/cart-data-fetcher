# Churn Predictor — Cart Abandonment Tool

Custom Opal tool for the churn predictor / re-engagement engine solution.
Simulates a query against an e-commerce backend for recent cart
abandonment events, structured for a "Risk Analyst" specialized agent
to consume and segment by churn probability.

## Run locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Verify it's working before touching Opal at all:

```bash
curl http://localhost:8000/discovery
curl -X POST http://localhost:8000/tools/get_cart_abandonment_data \
  -H "Content-Type: application/json" \
  -d '{"lookback_days": 7, "limit": 5}'
```

## Expose with ngrok

```bash
ngrok http 8000
```

Copy the HTTPS forwarding URL ngrok prints (e.g. `https://abc123.ngrok.io`).

## Tool parameters

| Param | Type | Default | Notes |
|---|---|---------|---|
| `lookback_days` | int | 7       | how far back to pull abandonment events |
| `min_cart_value` | float (optional) | none    | filter out low-value carts |
| `limit` | int | 20      | max records returned |
