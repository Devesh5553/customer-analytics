from fastapi import APIRouter

from backend.services.insight_service import (
    generate_insights
)

router = APIRouter()

@router.get("/insights")
async def insights():

    return await generate_insights()