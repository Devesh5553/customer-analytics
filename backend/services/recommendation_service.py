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

        return PRODUCTS["electronics"]

    elif segment == "High Value Customer":

        return PRODUCTS["gaming"]

    elif segment == "Frequent Buyer":

        return PRODUCTS["budget"]

    return PRODUCTS["budget"][:2]