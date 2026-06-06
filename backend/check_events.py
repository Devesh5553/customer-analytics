from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")

db = client["customer_ai"]

events = list(
    db.events.find().limit(5)
)

for event in events:
    print(event)