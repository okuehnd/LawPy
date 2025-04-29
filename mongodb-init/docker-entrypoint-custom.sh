#!/bin/bash
set -e

# Start MongoDB in the background
mongod --bind_ip_all &
MONGO_PID=$!

# Wait for MongoDB to start
echo "Waiting for MongoDB to start..."
sleep 10

# Import data
echo "Starting data import process..."

# Function to import a collection
import_collection() {
    collection_name=$1
    file_name=$2
    
    if [ -f "/data/import/$file_name" ]; then
        echo "Importing $collection_name collection..."
        mongoimport --db lawpy --collection "$collection_name" --file "/data/import/$file_name" --drop
        echo "$collection_name import completed!"
        return 0
    else
        echo "Warning: $file_name file not found!"
        return 1
    fi
}

# Import collections
import_collection "document_entities" "document_entities.json"
import_collection "keyword_postings" "keyword_postings.json"

# Run the index creation script
echo "Creating indexes..."
mongosh --file /docker-entrypoint-initdb.d/02-create-indexes.js

echo "Data import and index creation completed!"

# Keep the container running
echo "MongoDB is now running..."
wait $MONGO_PID 