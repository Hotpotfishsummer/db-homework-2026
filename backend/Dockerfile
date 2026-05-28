FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend /app/backend
COPY db /app/db

ENTRYPOINT ["/bin/sh", "/app/backend/entrypoint.sh"]
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "backend/main.py", "--host", "0.0.0.0", "--port", "8000"]