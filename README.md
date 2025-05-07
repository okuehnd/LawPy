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
- Build and start MongoDB, Django, and React containers.
- Import your data into MongoDB (if not already present).
- Create indexes for fast search.

---

### 3. Access the App

- **Frontend:** [http://localhost:3000](http://localhost:3000)  
  (React app, main user interface)
- **Backend API:** [http://localhost:8000](http://localhost:8000)  
  (Django REST API, see endpoints below)
- **MongoDB:** Accessible on port 27017 (for admin/debug)

---

## API Endpoints

The Django backend exposes two key endpoints (see `backend/urls.py`):

- `POST /api/SubmitQuery` — Submit a legal search query (returns results)
- `GET /api/results/` — Paginated search results


---

## Data Persistence

- MongoDB data is stored in a Docker volume named `mongodb_data`.
- Data will **persist** across container restarts.
- To remove all data, run:  
  ```bash
  docker compose down -v
  ```

---

## Development Notes

- **Frontend:**  
  Located in `LawPy/frontend` (React, Create React App, MUI).  
  Dockerfile builds and serves the static app on port 3000.

- **Backend:**  
  Located in `LawPy` (Django, DRF, MongoDB via PyMongo/Djongo).  
  Dockerfile runs Django on port 8000.

- **MongoDB:**  
  Custom Dockerfile loads data from `/data/import` (mapped from `./data`).  
  Indexes are created automatically on first run.

---

## Environment Variables

- Backend uses `.env` for secrets (see `docker-compose.yml`).
- MongoDB host is set via `MONGODB_HOST=mongodb` for internal networking.

---

## Stopping & Cleaning Up

- To stop all containers (but keep data):  
  ```bash
  docker compose down
  ```
- To stop and **remove all data**:  
  ```bash
  docker compose down -v
  ```

---

## Project Structure

- `data/` — Place your JSON data files here
- `LawPy/` — Django backend and project root
- `LawPy/frontend/` — React frontend
- `mongodb-init/` — MongoDB import and index scripts
- `docker-compose.yml` — Multi-container orchestration

---

## Troubleshooting

- If you change your data files and want to reload them, remove the volume:
  ```bash
  docker compose down -v
  docker compose up -d
  ```
- Check logs with:
  ```bash
  docker compose logs -f
  ``` 