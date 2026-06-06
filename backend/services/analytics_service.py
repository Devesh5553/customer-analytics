from backend.database.mongodb import db

async def get_user_summary(user_id: int):

    events = await db.events.find(
        {"user_id": user_id}
    ).to_list(length=None)

    total_events = len(events)

    purchases = sum(
        1 for e in events
        if e["event_type"] == "purchase"
    )

    total_spent = sum(
        e.get("price", 0)
        for e in events
        if e["event_type"] == "purchase"
    )

    return {
        "user_id": user_id,
        "total_events": total_events,
        "purchases": purchases,
        "total_spent": round(total_spent, 2)
    }