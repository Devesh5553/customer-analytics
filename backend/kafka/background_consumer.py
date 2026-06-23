# backend/kafka/background_consumer.py
import threading
import json
import asyncio
from kafka import KafkaConsumer
from pymongo import MongoClient
from backend.config import MONGO_URI, DATABASE_NAME
from backend.utils.websocket_manager import manager

def run_kafka_consumer(loop: asyncio.AbstractEventLoop):
    print("Starting background Kafka consumer thread...")
    try:
        # Establish a synchronous PyMongo connection for the thread execution
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        events_collection = db["events"]

        consumer = KafkaConsumer(
            "user_events",
            bootstrap_servers="localhost:9092",
            auto_offset_reset="latest",
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
            api_version=(3, 6, 0)
        )
        print("Kafka Consumer successfully subscribed to 'user_events' topic.")

        for message in consumer:
            event = message.value
            
            # Serialize Mongo details if any exist
            if '_id' in event:
                event['_id'] = str(event['_id'])
            
            # Insert into database synchronously
            events_collection.insert_one(event)
            
            # Remove any raw Mongo ID before sending over websockets
            if '_id' in event:
                del event['_id']

            # Safely schedule the broadcast in FastAPI's main event loop
            asyncio.run_coroutine_threadsafe(
                manager.broadcast(event),
                loop
            )
    except Exception as e:
        print(f"Error in background Kafka consumer: {e}")

def start_background_consumer():
    loop = asyncio.get_running_loop()
    thread = threading.Thread(target=run_kafka_consumer, args=(loop,), daemon=True)
    thread.start()
    print("Background consumer thread spawned.")
