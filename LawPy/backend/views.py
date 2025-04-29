from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from pymongo import MongoClient
import os
# from .models import 
# from .serializers import 

# Create your views here.
# class..(APIView):
#     def get(self,request):
#         #serialize response

#     def post(self,request):
#         #serialize requeset

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