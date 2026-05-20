FROM python:3.12-slim

# LibreOffice headless + шрифты с кириллицей для конвертации .docx → PDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    fonts-dejavu \
    fonts-liberation \
    fonts-noto-core \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Сначала зависимости (кэшируется при rebuild)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Шаблон договора
COPY templates/ ./templates/

# Потом код
COPY app.py .

EXPOSE 8082

# Папка под LibreOffice profile (нужна с правом записи)
ENV HOME=/tmp

# gunicorn для прод-режима: 2 воркера, 4 потока, timeout 120s
CMD ["gunicorn", "--bind", "0.0.0.0:8082", "--workers", "2", "--threads", "4", "--timeout", "120", "app:app"]
