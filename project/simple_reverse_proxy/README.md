# simple_reverse_proxy

This sample demonstrates using **nginx** as a reverse proxy in front of a small FastAPI backend.

## Usage

1. Build and start the containers:
   ```bash
   docker-compose up --build
   ```
2. Open `http://localhost` in your browser. Click the "取得" button to fetch data from the backend.

The backend will respond with the plain string `AAA`.

## Structure

- `backend/` - FastAPI application and Dockerfile
- `frontend/` - Static HTML/JavaScript served by nginx
- `nginx/` - nginx configuration
- `docker-compose.yml` - compose file running nginx and the backend
