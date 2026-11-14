# CampusConnect – CO3 Cloud Collaboration Prototype

A runnable local prototype for the CSA15 Cloud Computing and Big Data Analytics Assignment 3 (CO3). It demonstrates browser access, responsive layout, REST API access, shared placement records, role-based restrictions, and automated tests.

## Requirements
- Python 3.9 or later
- No third-party Python packages required

## Run

### Windows
```bat
run.bat
```

### Linux / macOS
```bash
chmod +x run.sh
./run.sh
```

Then open http://127.0.0.1:8000 in a browser.

## Demonstrations
- Browser application: `/`
- API request 1: `GET /api/health`
- API request 2: `GET /api/opportunities`
- Shared tasks: `GET /api/tasks`
- Role login: `POST /api/login` with JSON `{"role":"faculty"}`
- Restricted endpoint: `GET /api/admin` (403 without Placement Officer role)
- Task creation: `POST /api/tasks` with JSON `{"title":"Review placement plan"}` after logging in as `faculty`

## Python API client
Start the server in one terminal, then run `python app/api_client.py` in a second terminal. The client performs two GET requests and prints their HTTP status codes and JSON responses.

## Automated tests
Run `python -m unittest discover -s tests -v` while the server is not already running. The test suite starts and stops its own server and checks API responses, role access, and task creation.

## Data
The SQLite database is created automatically at `app/placement_demo.db` when the server starts. Delete this file to reset the sample data.

## Scope and deployment note
This is a local educational prototype. It demonstrates cloud-access concepts and cloud-application patterns but is not deployed to AWS or Google Cloud. A production deployment should use managed identity, HTTPS, secure secret management, a managed database, object storage, audit logging, backups, and a production-grade session store.
