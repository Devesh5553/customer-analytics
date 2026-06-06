from fastapi import APIRouter

router = APIRouter()

@router.get("/recommendations/{user_id}")
async def get_recommendations(user_id: int):

    return {
        "user_id": user_id,
        "recommendations": [
            "Laptop",
            "Headphones",
            "Keyboard"
        ]
    }