# backend/test_ml.py
import os
import sys
from fastapi.testclient import TestClient
from pymongo import MongoClient

# Ensure project root is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app
from backend.config import MONGO_URI, DATABASE_NAME

def test_ml_retraining():
    print("\n--- Starting Day 7 ML Integration Test ---")
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]

    with TestClient(app) as test_client:
        print("1. Triggering ML Model Retraining (/ml/retrain)...")
        response = test_client.post("/ml/retrain")
        assert response.status_code == 200
        result = response.json()
        
        print(f"   API Response: {result}")
        assert "status" in result
        
        status = result["status"]
        if status == "success":
            print("   ✅ ML Retrain triggered and executed successfully!")
            assert "users_clustered" in result
            assert "segments_summary" in result
            
            # Double check database records count
            segments_count = db.user_segments.count_documents({})
            print(f"   Segments Collection holds {segments_count} profiles.")
            assert segments_count == result["users_clustered"]
            print("   ✅ DB segments count matches the API response stats.")
            
        elif status in ["no_data", "no_users"]:
            print("   ℹ️ Info: Retraining skipped as expected (No events/users in database).")
        else:
            raise AssertionError(f"Unexpected status: {status}")

    print("--- Day 7 ML Integration Test Complete: PASSED ---")
    return True

if __name__ == "__main__":
    test_ml_retraining()
