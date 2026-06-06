from fastapi import APIRouter

from backend.services.analytics_service import (
    get_user_summary
)

router = APIRouter()

@router.get("/user/{user_id}")

async def user_stats(user_id: int):

    return await get_user_summary(
        user_id
    )