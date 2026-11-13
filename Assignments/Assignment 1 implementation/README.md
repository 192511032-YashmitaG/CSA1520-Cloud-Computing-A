# University Student Records API — Cloud Computing POC

A small university-related service used to demonstrate application deployment, container configuration, functional validation and basic resource monitoring.

## Requirements
- Python 3.11+ for local execution, or Docker Engine + Docker Compose for container execution.
- The application uses only Python's standard library; no `pip install` is required.

## Run locally (actual service validation)
```bash
python app/app.py
```
Open `http://localhost:5000` in a browser. In another terminal:
```bash
python tests/test_api.py
curl http://localhost:5000/health
curl http://localhost:5000/api/students
curl http://localhost:5000/api/students/1
curl -i http://localhost:5000/api/students/999
curl http://localhost:5000/metrics
```

## Run using Docker (container proof-of-concept)
```bash
docker compose build
docker compose up -d
docker compose ps
docker stats university-student-api
```
Then run the same API tests. Container limits in `compose.yaml`: 1 CPU and 512 MB memory. Stop with `docker compose down`.

## API endpoints
| Method | Endpoint | Expected result |
|---|---|---|
| GET | `/health` | HTTP 200, service healthy |
| GET | `/api/students` | HTTP 200, sample student list |
| GET | `/api/students/1` | HTTP 200, one record |
| GET | `/api/students/999` | HTTP 404, student not found |
| GET | `/metrics` | HTTP 200, process uptime, request count and memory metric |

## Evidence included
- `evidence/screenshots/` — browser screenshots captured while the local API was running.
- `evidence/logs/` — actual functional and concurrent-request test output.

## Important evidence note
The current build environment did not have Docker Engine installed, and network access was unavailable to install it. Therefore, the included run and test evidence proves the API was executed locally, but it does **not** prove that a Docker container was built or running. To complete the Docker-specific screenshot required by the assignment, run the Docker commands above on a computer with Docker Desktop/Engine and capture `docker compose ps` and `docker stats`. Do not label the local-process screenshot as a Docker-container screenshot.

Sample student records are fictional and for academic demonstration only. This is not a production SIS and has no authentication or persistent database.
