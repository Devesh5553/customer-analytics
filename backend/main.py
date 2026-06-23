from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes.events import router as events_router
from backend.api.routes.analytics import router as analytics_router
from backend.api.routes.recommendations import router as recommendations_router
from backend.api.routes.features import router as features_router
from backend.api.routes.simulator import router as simulator_router
from backend.api.routes.ml import router as ml_router
from backend.utils.websocket_manager import manager


app = FastAPI()

@app.on_event("startup")
async def startup_event():
    from backend.database.mongodb import init_db
    await init_db()
    
    # Start background consumer thread to stream events
    from backend.kafka.background_consumer import start_background_consumer
    try:
        start_background_consumer()
    except Exception as e:
        print(f"Could not start background Kafka consumer: {e}")
        
    # Auto-start simulated Kafka telemetry at 2s interval
    from backend.kafka.simulator_controller import simulator
    try:
        simulator.start()
    except Exception as e:
        print(f"Could not start default telemetry simulator: {e}")

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
app.include_router(simulator_router)
app.include_router(ml_router)

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

from backend.api.routes.insights import (
    router as insights_router
)

app.include_router(
    insights_router
)

@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

@app.get("/")
def home():
    return {
        "message": "Customer Analytics AI Backend Running"
    }