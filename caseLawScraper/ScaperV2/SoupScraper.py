import requests
import pymongo
import time
import re
from bs4 import BeautifulSoup
import datetime

client = pymongo.MongoClient("mongodb://localhost:27017/") 
db = client["court_listener_db"]
collection = db["opinions"]

api_token = ""
headers = {
    'Authorization': f'Token {api_token}'
}

base_cluster_api = "https://www.courtlistener.com/api/rest/v4/opinions/"

successCount = 0
failCount = 0
emptyCount = 153
batch_id = 0
last_log_time = time.time()
start_time = datetime.datetime.fromtimestamp(last_log_time).strftime("%Y-%m-%d %H:%M:%S")
print("▶️ Start time: ",start_time)


for doc in collection.find({"batch": batch_id,"textBlock": {"$exists": False},"plainBlock" : {"$exists": False},"failedScrape" : {"$exists": False}}):
    url = doc["link"]
    match = re.search(r'/opinion/([^/]+)/', url)
    if not match:
        continue

    opinion_id = match.group(1)
    opinion_url = base_cluster_api + opinion_id + "/"

    try:
        opinion_res = requests.get(opinion_url, headers=headers)
        if opinion_res.status_code != 200:
            failCount += 1
            print("❌ Failed to fetch opinion: ",opinion_url)
            print("🟥 Fail count: ",failCount)
            
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"failedScrape": "True"}}
            ) 
            continue

        opinion_data = opinion_res.json()

        plainText = opinion_data.get("plain_text") 
        if not plainText:
            plainText = opinion_data.get("html_with_citations", "")
        
        if not plainText:
            plainText = opinion_data.get("xml_harvard","")

        if not plainText:
            emptyCount += 1

            print("⚠️ No text found in opinion: ", opinion_url)
            print("◻️ Empty Count: ",emptyCount)
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"textBlock": " "}}
            ) 
            continue



        result = collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"plainBlock": str(plainText)}}
        )

        if result.modified_count == 0:
            print(f"⚠️ Document not updated for {opinion_id}")

        successCount += 1
        if successCount % 50 == 0:
            now = time.time()
            elapsed = now - last_log_time
            print(f"Scraper 1 ✅ Opinions saved: {successCount} | ⏱️ Time since last: {elapsed:.2f} seconds")
            last_log_time = now

        time.sleep(0.7)

    except Exception as e:
        print("⚠️ Error:", e)

print("☀️PROGRAM FINISHED☀️")
print("🟢 Success Count: ",successCount)
print("🟡 Empty Count: ",emptyCount)
print("🔴 Fail Count: ",failCount)

