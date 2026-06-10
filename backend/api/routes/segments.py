from fastapi import APIRouter
from pymongo import MongoClient

router = APIRouter()

client = MongoClient(
    "mongodb://localhost:27017"
)

db = client["customer_ai"]

@router.get("/segments")

async def get_segments():

    data = list(
        db.user_segments.find(
            {},
            {"_id": 0}
        )
    )

    return data


@router.get("/top-segments")
async def top_segments():

    pipeline = [
        {
            "$group": {
                "_id": "$segment",
                "count": {"$sum": 1}
            }
        }
    ]

    results = []

    for doc in db.user_segments.aggregate(
    pipeline
):
        results.append(doc)

    return results