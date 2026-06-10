# backend/ml/clustering.py

import pandas as pd
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")

db = client["customer_ai"]

events = list(db.events.find())


from collections import defaultdict

users = defaultdict(
    lambda: {
        "total_events": 0,
        "purchase_count": 0,
        "total_spent": 0
    }
)

for e in events:

    uid = e["user_id"]

    users[uid]["total_events"] += 1

    if e["event_type"] == "purchase":

        users[uid]["purchase_count"] += 1

        users[uid]["total_spent"] += e.get(
            "price",
            0
        )

df = pd.DataFrame.from_dict(
    users,
    orient="index"
)

df.index.name = "user_id"

df.reset_index(
    inplace=True
)

from sklearn.cluster import KMeans

features = df[
    [
        "total_events",
        "purchase_count",
        "total_spent"
    ]
]

model = KMeans(
    n_clusters=4,
    random_state=42
)

df["cluster"] = model.fit_predict(
    features
)

print(
    df.groupby("cluster").mean()
)

segment_names = {
    0: "Window Shopper",
    1: "Frequent Buyer",
    2: "High Value Customer",
    3: "Power User"
}

df["segment"] = df[
    "cluster"
].map(segment_names)

segments = db.user_segments

segments.delete_many({})

for row in df.to_dict(
    orient="records"
):

    segments.insert_one(row)

print(df["segment"].value_counts())

from pymongo import MongoClient

client = MongoClient(
    "mongodb://localhost:27017"
)

db = client["customer_ai"]

for doc in db.user_segments.find().limit(5):

    print(doc)