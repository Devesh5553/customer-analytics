from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017")
db = client["customer_ai"]
print(db.list_collection_names())