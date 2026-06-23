from fastapi import APIRouter
from backend.models.event_model import CustomerEvent
from backend.database.mongodb import db

router = APIRouter()

@router.post("/events")
async def create_event(event: CustomerEvent):

    event_dict = event.dict()

    await db.events.insert_one(event_dict)

    return {
        "message": "Event stored successfully"
    }