from fastapi import APIRouter
from backend.database.mongodb import db

router = APIRouter()

@router.get("/analytics")

async def analytics():

    total_events = await db.events.count_documents({})

    purchases = await db.events.count_documents(
        {"event_type": "purchase"}
    )

    return {
        "total_events": total_events,
        "purchases": purchases
    }