#!/bin/bash
set -e

echo "Waiting for MongoDB to start..."
sleep 5

echo "Starting data import process..."

# Only import document_entities.json and keyword_postings.json, explicitly skipping other files

# Import document_entities.json first (smaller file)
if [ -f /data/import/document_entities.json ]; then
  echo "Importing document_entities collection..."
  mongoimport --db lawpy --collection document_entities --file /data/import/document_entities.json --drop
  echo "Document entities import completed!"
else
  echo "Warning: document_entities.json file not found!"
fi

# Import keyword_postings.json (larger file)
if [ -f /data/import/keyword_postings.json ]; then
  echo "Importing keyword_postings collection..."
  mongoimport --db lawpy --collection keyword_postings --file /data/import/keyword_postings.json --drop
  echo "Keyword postings import completed!"
else
  echo "Warning: keyword_postings.json file not found!"
fi

echo "Data import completed!" 