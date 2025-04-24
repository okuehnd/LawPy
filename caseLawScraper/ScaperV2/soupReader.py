import requests
import pymongo
import time
import re
from bs4 import BeautifulSoup

client = pymongo.MongoClient("mongodb://localhost:27017/") 
db = client["court_listener_db"]
collection = db["opinions"]

successCount = 0
failCount = 0
emptyCount = 0

for doc in collection.find({"plainBlock" : {"$exists": True}}):
    # if successCount == 1:
    #     break
    soupText = doc['plainBlock']
    soup = BeautifulSoup(soupText,"html.parser")
    paragraphs = [p.get_text() for p in soup.find_all('p')]
    text_only = ' '.join(paragraphs)

    # print("🌟",text_only)
    if text_only:
        collection.update_one(
            {"_id": doc["_id"]},
            {
                "$set": {"textBlock": text_only},
                "$unset": {"plainBlock": ""}
            }
        )

    if successCount % 50 == 0:
            print(f"✅ Opinions saved: {successCount} ")
                  
    successCount += 1

print("🎊Finished: ",successCount)

