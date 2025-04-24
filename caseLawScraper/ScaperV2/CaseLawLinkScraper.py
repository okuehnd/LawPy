import requests
import time
import pymongo
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timedelta

client = pymongo.MongoClient("mongodb://localhost:27017/") 
db = client["court_listener_db"]
collection = db["opinions"]
progress_collection = db["scraper_progress"]
collection.create_index("link", unique=True)

base_api = "https://www.courtlistener.com/api/rest/v4/search/"
api_token =  "523cda014147845ab345204fc754d97a75a050f4"
headers = {
    'Authorization': f'Token {api_token}'
}

next_url = base_api  # start with the base search URL
collected = 113300
count = 0

start_date_str = progress_collection.find_one({"task": "courtlistener_ny"})
if start_date_str:
    start_date = datetime.strptime(start_date_str["last_date"], "%Y-%m-%d")
else:
    start_date = datetime(2000, 1, 1)

end_date = datetime.today()
step_days = 10  # adjust as needed

# Loop through date ranges
while start_date < end_date:
    next_date = start_date + timedelta(days=step_days)

    params = {
        "type":"o",
        "stat_Published": "on",
        "filed_after": start_date.strftime("%Y-%m-%d"),
        "filed_before": next_date.strftime("%Y-%m-%d"),
        "court": "ny nyappdiv nyappterm nysupct nycountyct nydistct nyjustct nyfamct nysurct nycivct nycrimct nyag",
        "ordering": "date_filed",
        "page_size": 20,
    }

    url = "https://www.courtlistener.com/api/rest/v4/search/"
    print(f"\n🔄 Fetching date range: {start_date.date()} to {next_date.date()}")

    while url:
        response = requests.get(url, headers=headers, params=params if '?' not in url else None)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])

            for item in results:
                opinion = {
                    "link": "https://www.courtlistener.com" + item["absolute_url"],
                    "title": item["caseName"]
                }
                try:
                    collection.insert_one(opinion)
                    collected += 1
                except pymongo.errors.DuplicateKeyError:
                    print(f"⚠️ Duplicate skipped: {opinion['link']}")

            url = data.get("next")  # follow deep pagination
            time.sleep(1)
        else:
            print(f"❌ Failed to fetch: {url}")
            print(response.text)
            break

    # Save progress
    progress_collection.update_one(
        {"task": "courtlistener_ny"},
        {"$set": {"last_date": next_date.strftime("%Y-%m-%d")}},
        upsert=True
    )
    start_date = next_date + timedelta(days=1)
    print(f"✅ Total collected: {collected} links")

# 🎉 Done
print(f"\n✅ Finished. Last date scraped: {start_date.date()}")