from fastapi import APIRouter

from backend.services.recommendation_service import (
    get_recommendations
)

router = APIRouter()

@router.get(
    "/recommendations/{user_id}"
)

async def recommendations(
    user_id: int
):

    recs = await get_recommendations(
        user_id
    )

    return {
        "user_id": user_id,
        "recommendations": recs
    }
# backend/services/recommendation_service.py

from backend.data.products import PRODUCTS
from backend.database.mongodb import db

async def get_recommendations(user_id):

    user = await db.user_segments.find_one(
        {"user_id": user_id}
    )

    if not user:
        return []

    segment = user["segment"]

    if segment == "VIP Customer":
        recs = PRODUCTS["electronics"]

    elif segment == "High Value Customer":
        recs = PRODUCTS["gaming"]

    elif segment == "Frequent Buyer":
        recs = PRODUCTS["budget"]

    else:
        recs = PRODUCTS["budget"][:2]

    # SAVE TO MONGODB
    await db.recommendations.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "user_id": user_id,
                "segment": segment,
                "recommendations": recs
            }
        },
        upsert=True
    )

    return recs