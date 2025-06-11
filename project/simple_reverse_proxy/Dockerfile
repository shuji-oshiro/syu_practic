FROM python:3.11-slim
WORKDIR /app

RUN pip install uv
COPY pyproject.toml .
COPY backend/app.py .
RUN uv pip install --system .
# CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
