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

## Register with Opal (once you have access)

1. Go to Opal → Tools Registry → "Add Tool Registry"
2. Registry URL: `<your-ngrok-url>/discovery`
3. Name: "Churn Predictor - Cart Abandonment Tool"
4. Save, then confirm `get_cart_abandonment_data` shows up as a discovered tool
5. Test it directly from Opal Chat by asking something like
   "get recent cart abandonment data for the last 7 days"

## Tool parameters

| Param | Type | Default | Notes |
|---|---|---|---|
| `lookback_days` | int | 14 | how far back to pull abandonment events |
| `min_cart_value` | float (optional) | none | filter out low-value carts |
| `limit` | int | 20 | max records returned |

## Notes for the write-up

- This mocks the data layer (as the test explicitly allows) but is
  structured exactly as a real ODP or e-commerce platform query would
  return it, so swapping in a real API later is a drop-in replacement,
  not a redesign.
- `summary` block is included alongside `records` specifically so the
  Risk Analyst agent doesn't have to do aggregate math itself before
  reasoning about the segment.
