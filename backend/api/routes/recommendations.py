from fastapi import APIRouter

from backend.services.recommendation_v2 import (
    recommend
)
from backend.services.recommendation_v2 import (
    recommend,
    explain_recommendation
)
router = APIRouter()

@router.get(
    "/recommendations/{user_id}"
)
async def get_recommendations(
    user_id: int
):

    recs = await recommend(
        user_id
    )

    return {
        "user_id": user_id,
        "recommendations": recs
    }
@router.get("/explain-recommendation/{user_id}")
async def explain(user_id: int):

    result = await explain_recommendation(
        user_id
    )

    return result