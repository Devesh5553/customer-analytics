from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes.events import router as events_router
from backend.api.routes.analytics import router as analytics_router
from backend.api.routes.recommendations import router as recommendations_router
from backend.api.routes.features import router as features_router


app = FastAPI()

# React frontend connection
origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(events_router)
app.include_router(analytics_router)
app.include_router(recommendations_router)

from backend.api.routes.user_analytics import (
    router as user_router
)

app.include_router(user_router)

app.include_router(features_router)

from backend.api.routes.segments import (
    router as segments_router
)

app.include_router(
    segments_router
)

from backend.api.routes.recommendations import (
    router as recommendations_router
)

app.include_router(
    recommendations_router
)

@app.get("/")
def home():
    return {
        "message": "Customer Analytics AI Backend Running"
    }