from fastapi import APIRouter

from backend.services.features import (
    build_user_features
)

router = APIRouter()

@router.get("/features")

async def features():

    return await build_user_features()