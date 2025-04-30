# LawPy MongoDB Container

This project sets up a MongoDB container that loads two collections on launch:
- `keyword_postings.json` (12.2GB) - Contains keyword-document mappings
- `document_entities.json` (21.4MB) - Contains document metadata with an index on the `id` field

## Prerequisites

- Docker and Docker Compose installed on your machine
- Your JSON data files in the `./data` directory

## Getting Started

1. Clone this repository
2. Make sure your data files are in the `./data` directory
3. Build and start the MongoDB container:

```bash
docker compose up -d
```

This will:
- Build the custom MongoDB image with database tools
- Start a MongoDB container
- Import your JSON data files into the MongoDB database
- Create indexes on the collections (this may take some time for larger collections)

## Testing the MongoDB Connection

You can connect to the MongoDB instance using the MongoDB shell:

```bash
docker exec -it lawpy-mongodb mongosh
```

Once connected, you can query the imported collections:

```javascript
use lawpy
db.keyword_postings.findOne()
db.document_entities.findOne()
```

To check the status of indexes:

```javascript
db.keyword_postings.getIndexes()
db.document_entities.getIndexes()
```

## Collection Details

### keyword_postings
- Size: 12.2GB
- Index: `keyword_idx` on the `keyword` field
- Structure: {keyword, id, count}
- Purpose: Maps keywords to document IDs and their occurrence counts

### document_entities
- Size: 21.4MB
- Index: `id_idx` on the `id` field
- Structure: Contains document metadata
- Purpose: Stores document information and relationships

## Adding a Frontend Container

The docker-compose.yml file includes a commented section for adding a frontend service (like Django) in the future. To enable it:

1. Create a frontend directory with your Django application
2. Uncomment the frontend service section in docker-compose.yml
3. Build and start the containers with `docker compose up -d`

## Connecting from Frontend to MongoDB

In your Django application, you'll be able to connect to MongoDB using the following connection string:

```
mongodb://mongodb:27017/lawpy
```

This uses the Docker service name "mongodb" as the hostname, which enables communication between containers on the same network.

## Data Persistence

MongoDB data is persisted in a Docker volume named `mongodb_data`. This ensures your data remains available even if the container is stopped or removed. 