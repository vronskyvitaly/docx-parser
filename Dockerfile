FROM python:3.12-slim

WORKDIR /app

# Сначала зависимости (кэшируется при rebuild)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Потом код
COPY app.py .

EXPOSE 8082

# gunicorn для прод-режима: 2 воркера, 4 потока, timeout 120s
CMD ["gunicorn", "--bind", "0.0.0.0:8082", "--workers", "2", "--threads", "4", "--timeout", "120", "app:app"]
