FROM ghcr.io/vronskyvitaly/docx-parser-base:latest

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY templates/ ./templates/
COPY app.py .

EXPOSE 8082

ENV HOME=/tmp

CMD ["gunicorn", "--bind", "0.0.0.0:8082", "--workers", "2", "--threads", "4", "--timeout", "120", "app:app"]
