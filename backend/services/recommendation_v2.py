from collections import Counter
from backend.database.mongodb import db

PRODUCT_CATALOG = {
    "electronics": [
        "MacBook Pro",
        "iPhone 17",
        "Samsung S26 Ultra",
        "Sony XM6"
    ],
    "gaming": [
        "PS5",
        "RTX 5080",
        "Xbox Series X",
        "Gaming Monitor"
    ],
    "budget": [
        "Boat Earbuds",
        "Redmi Note",
        "HP Keyboard",
        "Logitech Mouse"
    ]
}

async def get_user_preferences(user_id):

    categories = []

    cursor = db.events.find(
        {
            "user_id": user_id,
            "event_type": "purchase"
        }
    )

    async for doc in cursor:
        if "category" in doc:
            categories.append(doc["category"])

    return Counter(categories)

async def favorite_category(user_id):

    prefs = await get_user_preferences(user_id)

    if not prefs:
        return None

    return prefs.most_common(1)[0][0]

async def recommend(user_id):

    category = await favorite_category(user_id)

    if not category:
        return []

    return PRODUCT_CATALOG.get(category, [])

# XAI
from collections import Counter

async def explain_recommendation(user_id):

    prefs = await get_user_preferences(user_id)

    if not prefs:
        return {
            "user_id": user_id,
            "reason": "No purchase history found"
        }

    favorite = prefs.most_common(1)[0][0]

    total_purchases = sum(prefs.values())

    return {
        "user_id": user_id,
        "favorite_category": favorite,
        "purchase_count": total_purchases,
        "reason": f"User frequently purchases {favorite} products"
    }