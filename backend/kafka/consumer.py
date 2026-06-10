from kafka import KafkaConsumer
from pymongo import MongoClient
import json

consumer = KafkaConsumer(
    "user_events",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="latest",
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

mongo_client = MongoClient("mongodb://localhost:27017")

db = mongo_client["customer_ai"]

events_collection = db["events"]

print("Consumer Started...")

for message in consumer:

    event = message.value

    events_collection.insert_one(event)

    print(f"Stored: {event}")