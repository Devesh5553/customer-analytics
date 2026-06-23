# backend/services/recommendation_service.py
from backend.data.products import PRODUCTS
from backend.database.mongodb import db
from backend.services.recommendation_v2 import recommend as recommend_v2

async def get_recommendations(user_id):
    """
    Multi-tiered recommendation resolver:
    1. Try cluster segment recommendations (K-Means output)
    2. Fall back to dynamic interest category calculation based on purchase history
    3. Fall back to global popular defaults (cold-start)
    """
    user = await db.user_segments.find_one(
        {"user_id": user_id}
    )

    if user:
        segment = user.get("segment")
        if segment == "Power User":
            return PRODUCTS["electronics"]
        elif segment == "High Value Customer":
            return PRODUCTS["gaming"]
        elif segment == "Frequent Buyer":
            return PRODUCTS["budget"]
        elif segment == "Window Shopper":
            return PRODUCTS["budget"][:2]

    # Fallback 1: Dynamic categories computed from purchase history
    dynamic_recs = await recommend_v2(user_id)
    if dynamic_recs:
        return dynamic_recs

    # Fallback 2: Universal popular default (cold start)
    return PRODUCTS["budget"][:2]