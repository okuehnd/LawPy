from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.conf import settings
from pymongo import MongoClient
from openai import OpenAI
import json
import os
import logging

logger = logging.getLogger(__name__)
# from .models import 
# from .serializers import 

# Create your views here.
# class..(APIView):
#     def get(self,request):
#         #serialize response

#     def post(self,request):
#         #serialize requeset

# @csrf_exempt #add if doesnt work?


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

def search_documents(client: MongoClient, keywords, limit: int = 10, debug: bool = False):
    try:
        db = client["lawpy"]
        keywords_collection = db["keyword_postings"]
        documents_collection = db["document_entities"]

        # Print sample documents from each collection for debugging
        # if debug:
        #     print("\nSample keyword_postings document:")
        #     pprint.pprint(keywords_collection.find_one())
        #     print("\nSample document_entities document:")
        #     pprint.pprint(documents_collection.find_one())
            
        #     # Show counts for each keyword to verify they exist
        #     print("\nKeyword counts in collection:")
        #     for keyword in keywords:
        #         count = keywords_collection.count_documents({"keyword": keyword})
        #         print(f"  '{keyword}': {count} occurrences")

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

"""
THIS IS WHAT I KEEP GETTING !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
endpoint called
Raw response: {
  "keywords": [
    "divorce decree",
    "child custody",
    "property division",
    "spousal support",
    "alimony",
    "marital assets",
    "legal separation",
    "mediation",
    "court jurisdiction"
  ]
}
Error connecting to MongoDB: localhost:27017: [Errno 111] Connection refused (configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms), Timeout: 30s, Topology Description: <TopologyDescription id: 6811bb84de6dac5b2ff515cd, topology_type: Unknown, servers: [<ServerDescription ('localhost', 27017) server_type: Unknown, rtt: None, error=AutoReconnect('localhost:27017: [Errno 111] Connection refused (configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms)')>]>
Error in main execution: localhost:27017: [Errno 111] Connection refused (configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms), Timeout: 30s, Topology Description: <TopologyDescription id: 6811bb84de6dac5b2ff515cd, topology_type: Unknown, servers: [<ServerDescription ('localhost', 27017) server_type: Unknown, rtt: None, error=AutoReconnect('localhost:27017: [Errno 111] Connection refused (configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms)')>]>
Watching for file changes with StatReloader
"""

@csrf_exempt
@api_view(['POST'])
def SubmitQuery(request):
    logger.debug("endpoint called")
    print("END POINT CALLED")
    if request.method == 'POST':
        query = request.data.get('query')
        
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        prompt = f"""Role: You are a case-law search engine assistant.

            Task: From the user's question, extract 5-10 key legal search terms.

            Requirements:
            - Return ONLY a JSON array of lowercase keywords
            - No explanations or other text
            - Each term should be specific and useful for legal search
            - Avoid generic terms like "case" or "law" unless part of a specific phrase

            Input: {query}"""
        
        keywordSet = set()
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a legal keyword extractor. Respond only with a JSON object containing an array of keywords under the 'keywords' key."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4  # Lower temperature for more consistent output
            )
            # Get the response content
            content = response.choices[0].message.content
            print(f"Raw response: {content}")
            
            # Parse the JSON response
            response_data = json.loads(content)
            
            # Extract keywords from the response
            if isinstance(response_data, dict) and 'keywords' in response_data:
                keywords = response_data['keywords']
            elif isinstance(response_data, list):
                keywords = response_data
            else:
                print("Unexpected response format. Using empty set.")
                
            keywordSet = set(keywords) # Convert to set to remove any duplicates
            
        except Exception as e:
            print(f"Error in keyword extraction: {e}")
            return JsonResponse({'message': 'Keyword Extraction Error'}, status=400)
        
        try:
            client = connect_to_mongodb()
        
            
            results = search_documents(client, list(keywordSet))
            
            # print("\nSearch Results:")
            # print("==============")
            # for idx, result in enumerate(results, 1):
            #     print(f"\nResult {idx}:")
            #     pprint.pprint(result)
                
        except Exception as e:
            print(f"Error in main execution: {e}")
            return JsonResponse({'message': 'MongoDB Extraction Error'}, status=400)
        finally:
            if 'client' in locals():
                client.close()

        res = []
        for result in results:
            res.append({
                # 'docId': id,
                'title' : "Case",
                'url':result['url'],
            })
        
        print("RESULT ARRAY: ",res)
        if res:
            return JsonResponse({'message':'Query returned results successfully','results':res},status=200)
        return JsonResponse({'message' : 'No results','results':res},status = 200)
    return JsonResponse({'message': 'Invalid request'}, status=400)

@csrf_exempt
def TestView(request):
    logger.debug("GOT TEST VIEW")
    return JsonResponse({"message": "Hello from Django!"})

def test_mongodb(request):
    try:
        # Get MongoDB host from environment variable or default to localhost
        mongodb_host = os.environ.get('MONGODB_HOST', 'localhost')
        
        # Create a MongoDB client
        client = MongoClient(f'mongodb://{mongodb_host}:27017/')
        
        # Access the database
        db = client['lawpy']
        
        # Try to ping the database
        client.admin.command('ping')
        
        # Create a test collection and insert a document
        test_collection = db.test_collection
        test_document = {"test": "Hello from Django!", "timestamp": "test"}
        test_collection.insert_one(test_document)
        
        # Retrieve the document
        retrieved_doc = test_collection.find_one({"test": "Hello from Django!"})
        
        return JsonResponse({
            'status': 'success',
            'message': 'MongoDB connection successful',
            'test_document': {
                'test': retrieved_doc['test'],
                'timestamp': retrieved_doc['timestamp']
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'MongoDB connection failed: {str(e)}'
        }, status=500)