# backend/ml/clustering.py
import pandas as pd
from pymongo import MongoClient
from collections import defaultdict
from sklearn.cluster import KMeans
from backend.config import MONGO_URI, DATABASE_NAME

def run_kmeans_clustering():
    print("Starting KMeans clustering batch run...")
    try:
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        
        events = list(db.events.find())
        if not events:
            print("No events found in database. Skipping clustering.")
            return {"status": "no_data", "message": "No events found in database"}
            
        users = defaultdict(
            lambda: {
                "total_events": 0,
                "purchase_count": 0,
                "total_spent": 0
            }
        )

        for e in events:
            uid = e.get("user_id")
            if uid is None:
                continue
            users[uid]["total_events"] += 1
            if e.get("event_type") == "purchase":
                users[uid]["purchase_count"] += 1
                users[uid]["total_spent"] += e.get("price", 0)

        df = pd.DataFrame.from_dict(
            users,
            orient="index"
        )
        df.index.name = "user_id"
        df.reset_index(inplace=True)

        num_users = len(df)
        n_clusters = min(4, num_users)
        
        if n_clusters < 1:
            print("No user profiles created. Skipping clustering.")
            return {"status": "no_users", "message": "No users found"}

        features = df[["total_events", "purchase_count", "total_spent"]]

        # Scale features so that high-magnitude metrics (like total_spent) do not dominate the distance calculations
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)

        model = KMeans(
            n_clusters=n_clusters,
            random_state=42
        )
        df["cluster"] = model.fit_predict(scaled_features)

        # Smart labeling: Group by cluster and compute the average total spent.
        # Sort these cluster IDs by spent ascending to assign labels deterministically.
        cluster_means = df.groupby("cluster")["total_spent"].mean().sort_values()
        
        labels = ["Window Shopper", "Frequent Buyer", "High Value Customer", "Power User"]
        segment_names = {}
        for i, cluster_id in enumerate(cluster_means.index):
            segment_names[cluster_id] = labels[i]
            
        df["segment"] = df["cluster"].map(segment_names)

        segments = db.user_segments
        segments.delete_many({})
        
        records = df.to_dict(orient="records")
        if records:
            segments.insert_many(records)
            
        print(f"Clustered {num_users} users successfully.")
        print(df["segment"].value_counts().to_dict())
        
        return {
            "status": "success",
            "users_clustered": num_users,
            "segments_summary": df["segment"].value_counts().to_dict()
        }
    except Exception as e:
        print(f"Error during clustering execution: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    run_kmeans_clustering()