import requests
import pymongo
import time
import re
from bs4 import BeautifulSoup
from bson import ObjectId

client = pymongo.MongoClient("mongodb://localhost:27017/") 
db = client["court_listener_db"]
collection = db["opinions"]

batches = 8  # or however many instances/scripts you'll run
# all_docs = list(collection.find({
#     "$or": [
#         { "failedScrape": { "$exists": True } },
#         { "textBlock": { "$regex": "^\\s*$" } }
#     ]
# }))
all_docs = list(collection.find({}))
count = 0
for idx, doc in enumerate(all_docs):
    collection.update_one(
        {"_id": doc["_id"]},
        {"$set": {"batch": idx % batches}}
        # {"$set": {"batch": -1}}
    )
    count += 1
    if count % 10000 == 0:
        print("Count: ",count)

print("🌟 Batched Count: ",count)