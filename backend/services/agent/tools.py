from backend.database.mongodb import db


async def get_top_segments():

    pipeline = [
        {
            "$group": {
                "_id": "$segment",
                "count": {
                    "$sum": 1
                }
            }
        }
    ]

    result = []

    async for item in db.user_segments.aggregate(pipeline):
        result.append(item)

    return result



async def get_customer_recommendations(user_id):

    data = await db.recommendations.find_one(
        {
            "user_id": user_id
        }
    )

    return data