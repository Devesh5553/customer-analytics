# backend/api/routes/simulator.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.kafka.simulator_controller import simulator

router = APIRouter(prefix="/simulator", tags=["simulator"])

class SimulatorConfig(BaseModel):
    delay_seconds: float

@router.post("/start")
def start_simulator():
    success = simulator.start()
    if not success:
        return {"status": "already_running", "message": "Simulator is already active"}
    return {"status": "started", "message": "Simulator started"}

@router.post("/stop")
def stop_simulator():
    success = simulator.stop()
    if not success:
        return {"status": "already_stopped", "message": "Simulator is not active"}
    return {"status": "stopped", "message": "Simulator stopped"}

@router.post("/config")
def update_config(config: SimulatorConfig):
    if config.delay_seconds <= 0:
        raise HTTPException(status_code=400, detail="delay_seconds must be greater than 0")
    simulator.set_delay(config.delay_seconds)
    return {
        "status": "configured", 
        "delay_seconds": simulator.delay_seconds,
        "message": f"Delay updated to {simulator.delay_seconds}s"
    }

@router.get("/status")
def get_status():
    return {
        "is_running": simulator.is_running,
        "delay_seconds": simulator.delay_seconds
    }
