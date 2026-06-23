from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import MONGO_URI, DATABASE_NAME

client = AsyncIOMotorClient(MONGO_URI)

db = client[DATABASE_NAME]

async def init_db():
    # Index user_id for analytics filters and group aggregations
    await db.events.create_index([("user_id", 1)])
    # Index timestamp for time-sorted telemetry query performance
    await db.events.create_index([("timestamp", -1)])
    # Index user_id in user_segments for fast segment lookups
    await db.user_segments.create_index([("user_id", 1)], unique=True)