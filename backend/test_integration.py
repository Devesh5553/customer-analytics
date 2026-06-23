# backend/test_integration.py
import os
import sys
import time
import asyncio
from fastapi.testclient import TestClient
from pymongo import MongoClient

# Ensure the root of the project is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app
from backend.config import MONGO_URI, DATABASE_NAME
from backend.utils.websocket_manager import manager

def test_telemetry_flow():
    print("\n--- Starting Day 4 Integration Test ---")
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]

    # Use TestClient as context manager to run startup and shutdown lifespan events
    with TestClient(app) as test_client:
        print("1. FastAPI App started successfully (lifespan events run).")
        
        # Test 1: HTTP Root endpoint
        response = test_client.get("/")
        assert response.status_code == 200
        assert response.json()["message"] == "Customer Analytics AI Backend Running"
        print("  Basic HTTP GET / matches expectation.")

        # Test 2: HTTP Simulator Status endpoint
        status_res = test_client.get("/simulator/status")
        assert status_res.status_code == 200
        status_data = status_res.json()
        print(f"   Simulator Status: is_running={status_data['is_running']}, delay_seconds={status_data['delay_seconds']}")
        
        # Shut down simulator during test to avoid extra traffic interferences
        stop_res = test_client.post("/simulator/stop")
        print(f"   Stopping default telemetry simulator: {stop_res.json()}")

        # Test 3: WebSocket telemetry connection and broadcast dispatch
        print("2. Connecting to WebSocket /ws/telemetry...")
        try:
            with test_client.websocket_connect("/ws/telemetry") as websocket:
                print("    WebSocket connection established successfully.")

                print("3. Testing WebSocket broadcast message dispatch...")
                test_event = {
                    "user_id": 9999,
                    "event_type": "test_broadcast",
                    "product": "Test Pro",
                    "category": "test",
                    "price": 9.99
                }
                
                # Run the broadcast async function on the main event loop
                asyncio.run(manager.broadcast(test_event))
                
                # Attempt to receive payload
                data = websocket.receive_json()
                print(f"   Received message over WebSocket: {data}")
                assert data["user_id"] == 9999
                assert data["event_type"] == "test_broadcast"
                print("    WebSocket broadcast message matches the transmitted event.")
                
        except Exception as e:
            print(f"    WebSocket testing failed: {e}")
            raise e

    print("--- Day 4 Integration Test Complete: ALL PASSED ---")
    return True

if __name__ == "__main__":
    test_telemetry_flow()
