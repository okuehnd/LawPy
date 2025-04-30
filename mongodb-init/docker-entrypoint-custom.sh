#!/bin/bash
set -e

# Start MongoDB in the background
mongod --bind_ip_all &
MONGO_PID=$!

# Wait for MongoDB to start
echo "Waiting for MongoDB to start..."
sleep 10

# Check if collections already exist before importing
echo "Checking for existing collections..."

# Function to check if a collection exists and import if it doesn't
check_and_import_collection() {
    collection_name=$1
    file_name=$2
    
    # Check if collection exists and has documents
    collection_exists=$(mongosh --quiet --eval "db.getSiblingDB('lawpy').getCollectionNames().includes('$collection_name')" --norc | tr -d '\r')
    collection_count=0
    
    if [ "$collection_exists" = "true" ]; then
        collection_count=$(mongosh --quiet --eval "db.getSiblingDB('lawpy').$collection_name.countDocuments({})" --norc | tr -d '\r')
    fi
    
    echo "Collection '$collection_name' exists: $collection_exists, document count: $collection_count"
    
    if [ "$collection_exists" = "true" ] && [ "$collection_count" -gt 0 ]; then
        echo "Collection $collection_name already exists with $collection_count documents. Skipping import."
        return 0
    elif [ -f "/data/import/$file_name" ]; then
        echo "Importing $collection_name collection..."
        mongoimport --db lawpy --collection "$collection_name" --file "/data/import/$file_name" --drop
        echo "$collection_name import completed!"
        return 0
    else
        echo "Warning: $file_name file not found in /data/import/"
        return 1
    fi
}

# Check and import collections only if they don't exist
check_and_import_collection "document_entities" "document_entities.json"
check_and_import_collection "keyword_postings" "keyword_postings.json"

# Run the index creation script only if needed
echo "Ensuring indexes exist..."
mongosh --file /docker-entrypoint-initdb.d/02-create-indexes.js

echo "Data validation completed!"

# Keep the container running
echo "MongoDB is now running..."
wait $MONGO_PID 