from kafka import KafkaProducer
import json
import random
import time
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers=["127.0.0.1:9092"],
    api_version=(3, 6, 0),
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

PRODUCTS = [
    ("MacBook Pro", "electronics"),
    ("iPhone 17", "electronics"),
    ("PS5", "gaming"),
    ("RTX 5080", "gaming"),
    ("Boat Earbuds", "budget"),
    ("Logitech Mouse", "budget")
]



EVENT_TYPES = [
    "view_product",
    "add_to_cart",
    "purchase",
    "wishlist"
]

while True:
    product, category = random.choice(PRODUCTS)
    event = {
        "user_id": random.randint(1, 1000),
        "event_type": random.choice(EVENT_TYPES),
        "product": product,
        "category": category, 
        "product_id": random.randint(100, 999),
        "price": round(random.uniform(100, 50000), 2),
        "timestamp": datetime.utcnow().isoformat()
    }

    producer.send("user_events", event)

    print(event)

    time.sleep(2)