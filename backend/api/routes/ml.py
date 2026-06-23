# backend/api/routes/ml.py
from fastapi import APIRouter
from backend.ml.clustering import run_kmeans_clustering

router = APIRouter(prefix="/ml", tags=["ml"])

@router.post("/retrain")
def retrain_model():
    """
    Triggers the K-Means clustering batch calculation on-demand,
    re-aggregates user profiles, standardizes dimensions, segments them,
    and updates the database.
    """
    result = run_kmeans_clustering()
    return result
