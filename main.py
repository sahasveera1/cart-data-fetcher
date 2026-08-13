import random
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI
from opal_tools_sdk import ToolsService, tool
from pydantic import BaseModel, Field

app = FastAPI(title="Churn Predictor Tools")
tools_service = ToolsService(app)

# ---------------------------------------------------------------------------
# Mock database of customers with recent funnel activity.
# In production this would query ODP, a data warehouse, or an e-commerce
# platform's API (Shopify, BigCommerce, etc.) instead of returning static data.
# ---------------------------------------------------------------------------
_FIRST_NAMES = ["Jordan", "Casey", "Priya", "Miguel", "Aisha", "Noah", "Elena", "Sam"]
_LAST_NAMES = ["Reed", "Nguyen", "Patel", "Garcia", "Smith", "Kim", "Rossi", "Chen"]
_PRODUCT_CATEGORIES = ["footwear", "outerwear", "electronics", "home-goods", "beauty"]


def _generate_mock_customer(customer_id: int) -> dict:
    """Builds one synthetic cart-abandonment record with realistic signal
    fields a downstream analyst agent can use to score churn risk."""
    days_since_abandon = random.randint(0, 13)
    cart_value = round(random.uniform(25, 480), 2)
    prior_purchases = random.randint(0, 12)
    email_opens_last_30d = random.randint(0, 15)
    site_visits_last_30d = random.randint(1, 20)

    return {
        "customer_id": f"cust_{customer_id:05d}",
        "name": f"{random.choice(_FIRST_NAMES)} {random.choice(_LAST_NAMES)}",
        "email": f"customer{customer_id}@example.com",
        "cart_value_usd": cart_value,
        "cart_items": [
            {
                "category": random.choice(_PRODUCT_CATEGORIES),
                "quantity": random.randint(1, 3),
            }
            for _ in range(random.randint(1, 4))
        ],
        "days_since_abandonment": days_since_abandon,
        "abandoned_at": (
            datetime.utcnow() - timedelta(days=days_since_abandon)
        ).isoformat() + "Z",
        "prior_purchases_90d": prior_purchases,
        "email_opens_last_30d": email_opens_last_30d,
        "site_visits_last_30d": site_visits_last_30d,
        "is_returning_customer": prior_purchases > 0,
    }


class CartAbandonmentParams(BaseModel):
    lookback_days: int = Field(
        default=7, description="How many days back to include abandonment events for."
    )
    min_cart_value: Optional[float] = Field(
        default=None, description="Optional floor on cart value, to filter out low-value carts."
    )
    limit: int = Field(default=20, description="Max number of records to return.")


@tool(
    name="get_cart_abandonment_data",
    description=(
        "Fetches recent cart abandonment and funnel drop-off records for "
        "e-commerce customers, including cart value, items, recency, and "
        "engagement signals (email opens, site visits, purchase history). "
        "Use this to identify customers at risk of churning so they can be "
        "segmented and targeted with re-engagement campaigns."
    ),
)
async def get_cart_abandonment_data(parameters: CartAbandonmentParams) -> dict:
    """
    Returns a dict with a `records` list of abandonment events and a
    `summary` block giving quick aggregate stats, so the agent doesn't
    have to recompute them.
    """
    lookback_days = parameters.lookback_days
    min_cart_value = parameters.min_cart_value
    limit = parameters.limit

    random.seed(lookback_days * 1000 + limit)  # more deterministic mock data per call shape

    records = [_generate_mock_customer(i) for i in range(1, limit + 1)]
    records = [r for r in records if r["days_since_abandonment"] <= lookback_days]

    if min_cart_value is not None:
        records = [r for r in records if r["cart_value_usd"] >= min_cart_value]

    total_value = round(sum(r["cart_value_usd"] for r in records), 2)

    return {
        "summary": {
            "record_count": len(records),
            "total_abandoned_cart_value_usd": total_value,
            "lookback_days": lookback_days,
        },
        "records": records,
    }
