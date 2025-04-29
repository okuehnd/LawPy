from pymongo import MongoClient
import pprint
from typing import List
import sys

def connect_to_mongodb(host: str = "mongodb://localhost:27017") -> MongoClient:
    try:
        client = MongoClient(host)
        # Test the connection
        client.admin.command('ping')
        print("Successfully connected to MongoDB")
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise

def search_documents(client: MongoClient, keywords: List[str], limit: int = 10, debug: bool = False):
    try:
        db = client["lawpy"]
        keywords_collection = db["keyword_postings"]
        documents_collection = db["document_entities"]

        # Print sample documents from each collection for debugging
        if debug:
            print("\nSample keyword_postings document:")
            pprint.pprint(keywords_collection.find_one())
            print("\nSample document_entities document:")
            pprint.pprint(documents_collection.find_one())
            
            # Show counts for each keyword to verify they exist
            print("\nKeyword counts in collection:")
            for keyword in keywords:
                count = keywords_collection.count_documents({"keyword": keyword})
                print(f"  '{keyword}': {count} occurrences")

        # First pipeline to get matching documents
        pipeline = [
            {
                "$match": {
                    "keyword": {"$in": keywords}
                }
            },
            {
                "$group": {
                    "_id": "$id",  # Group by the document id field
                    "id": {"$first": "$id"},  # Preserve the id field for matching
                    "matchedKeywords": {"$addToSet": "$keyword"},
                    "totalScore": {"$sum": "$count"}
                }
            },
            {
                "$addFields": {
                    "distinctMatches": {"$size": "$matchedKeywords"}
                }
            },
            {
                "$sort": {
                    "distinctMatches": -1,  # First by number of distinct keywords matched
                    "totalScore": -1        # Then by total count (frequency)
                }
            },
            {
                "$limit": limit
            }
        ]

        # Execute first pipeline to get top documents
        matched_docs = list(keywords_collection.aggregate(pipeline))

        if debug:
            print("\nAggregation pipeline results (before URL lookup):")
            for doc in matched_docs:
                print(f"ID: {doc['id']}, Keywords: {doc['matchedKeywords']}, Score: {doc['totalScore']}")

        if not matched_docs:
            print("No matching documents found")
            return []

        # Get document IDs from the matched documents
        doc_ids = [doc["id"] for doc in matched_docs]

        # Second query to get URLs for the matched document IDs
        url_docs = list(documents_collection.find(
            {"id": {"$in": doc_ids}},
            {"id": 1, "url": 1, "_id": 0}
        ))
        
        if debug:
            print("\nDocument URLs found:")
            for doc in url_docs:
                print(f"ID: {doc['id']}, URL: {doc['url']}")

        # Create a mapping of document ID to URL
        url_mapping = {doc["id"]: doc["url"] for doc in url_docs}

        # Combine results
        final_results = []
        for doc in matched_docs:
            if doc["id"] in url_mapping:
                final_results.append({
                    "docId": doc["id"],
                    "url": url_mapping[doc["id"]],
                    "distinctMatches": doc["distinctMatches"],
                    "totalScore": doc["totalScore"],
                    "matchedKeywords": doc["matchedKeywords"]
                })

        return final_results

    except Exception as e:
        print(f"Error executing search: {e}")
        raise

def main():
    # Enable debug mode with command line argument
    debug_mode = "--debug" in sys.argv
    
    # Test keywords - can be overridden from command line
    test_keywords = ["child custody", "divorce", "father"]
    
    # Allow command line keyword arguments
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        test_keywords = sys.argv[1:]
        print(f"Using command line keywords: {test_keywords}")
    
    try:
        client = connect_to_mongodb()
        
        if debug_mode:
            print(f"\nSearching for keywords: {test_keywords}")
        
        results = search_documents(client, test_keywords, debug=debug_mode)
        
        print("\nSearch Results:")
        print("==============")
        for idx, result in enumerate(results, 1):
            print(f"\nResult {idx}:")
            pprint.pprint(result)
            
    except Exception as e:
        print(f"Error in main execution: {e}")
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    main() 