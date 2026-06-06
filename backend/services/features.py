from backend.database.mongodb import db

async def build_user_features():

    pipeline = [
        {
            "$group": {
                "_id": "$user_id",
                "total_events": {
                    "$sum": 1
                },
                "avg_price": {
                    "$avg": "$price"
                },
                "purchase_count": {
                    "$sum": {
                        "$cond": [
                            {
                                "$eq": [
                                    "$event_type",
                                    "purchase"
                                ]
                            },
                            1,
                            0
                        ]
                    }
                }
            }
        }
    ]

    return await db.events.aggregate(
        pipeline
    ).to_list(None)