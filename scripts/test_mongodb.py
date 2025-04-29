#!/usr/bin/env python3
"""
Test script to verify MongoDB connection and data loading
"""
import pymongo
import json
from bson import json_util
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

def test_mongodb_connection():
    """Test connection to MongoDB and verify collections"""
    try:
        # Connect to MongoDB
        print("Attempting to connect to MongoDB...")
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        
        # Check connection
        try:
            client.admin.command('ismaster')
            print("Successfully connected to MongoDB")
        except (ConnectionFailure, ServerSelectionTimeoutError):
            print("MongoDB is not ready yet. Please try again later.")
            return
        
        # Access database
        db = client["lawpy"]
        
        # List all collections
        collections = db.list_collection_names()
        print(f"Available collections: {collections}")
        
        # Check if data is loaded
        if "keyword_postings" in collections and "document_entities" in collections:
            keyword_count = db.keyword_postings.count_documents({})
            entities_count = db.document_entities.count_documents({})
            
            if keyword_count > 0 and entities_count > 0:
                print(f"Data import complete! Found {keyword_count} keyword postings and {entities_count} document entities")
                
                # Print sample documents
                sample = db.keyword_postings.find_one()
                if sample:
                    print("Sample document from keyword_postings:")
                    print(json.dumps(json.loads(json_util.dumps(sample)), indent=2))
                
                sample = db.document_entities.find_one()
                if sample:
                    print("Sample document from document_entities:")
                    print(json.dumps(json.loads(json_util.dumps(sample)), indent=2))
            else:
                print("MongoDB is running but data import is still in progress.")
                print(f"Current status: {keyword_count} keyword postings and {entities_count} document entities")
        else:
            print("MongoDB is running but collections are not yet created. Data import may still be in progress.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_mongodb_connection() 