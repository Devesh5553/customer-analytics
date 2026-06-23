# backend/kafka/simulator_controller.py
import threading
import time
import random
import json
from datetime import datetime
from kafka import KafkaProducer
from backend.config import MONGO_URI

PRODUCTS = [
    ("MacBook Pro", "electronics"),
    ("iPhone 17 Pro", "electronics"),
    ("Sony WH-1000XM6", "electronics"),
    ("Samsung S26 Ultra", "electronics"),
    ("Redmi Note", "budget"),
    ("Boat Earbuds", "budget"),
    ("Logitech Mouse", "budget"),
    ("HP Keyboard", "budget"),
    ("PS5", "gaming"),
    ("RTX 5080", "gaming"),
    ("Xbox Series X", "gaming"),
    ("Gaming Monitor", "gaming")
]

EVENT_TYPES = [
    "view_product",
    "add_to_cart",
    "purchase",
    "wishlist"
]

class TelemetrySimulator:
    def __init__(self):
        self.is_running = False
        self.delay_seconds = 2.0
        self.thread = None
        self._stop_event = threading.Event()
        self.producer = None

    def _init_producer(self):
        if not self.producer:
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=["127.0.0.1:9092"],
                    api_version=(3, 6, 0),
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                    request_timeout_ms=5000
                )
                print("Simulator Kafka connection successfully established.")
            except Exception as e:
                print(f"Simulator failed to connect to Kafka: {e}")
                self.producer = None

    def _loop(self):
        self._init_producer()
        if not self.producer:
            print("Simulator thread exiting because Kafka connection failed.")
            self.is_running = False
            return

        print("Telemetry simulator thread started running loop.")
        while not self._stop_event.is_set():
            try:
                product, category = random.choice(PRODUCTS)
                event = {
                    "user_id": random.randint(1, 1000),
                    "event_type": random.choice(EVENT_TYPES),
                    "product": product,
                    "category": category, 
                    "product_id": random.randint(100, 999),
                    "price": round(random.uniform(10, 2000), 2),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                self.producer.send("user_events", event)
                print(f"[SIMULATOR] Produced: {event}")
            except Exception as e:
                print(f"[SIMULATOR] Error producing event: {e}")
            
            # Sleep in short steps so the loop shuts down instantly when stopped
            sleep_elapsed = 0.0
            step = 0.1
            while sleep_elapsed < self.delay_seconds:
                if self._stop_event.is_set():
                    break
                time.sleep(step)
                sleep_elapsed += step

        print("Telemetry simulator loop stopped.")
        self.is_running = False

    def start(self):
        if self.is_running:
            return False
        
        self.is_running = True
        self._stop_event.clear()
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        return True

    def stop(self):
        if not self.is_running:
            return False
        
        self._stop_event.set()
        if self.thread:
            self.thread.join(timeout=2.0)
        self.is_running = False
        return True

    def set_delay(self, seconds: float):
        self.delay_seconds = max(0.1, seconds)  # Max 10 events/sec

simulator = TelemetrySimulator()
