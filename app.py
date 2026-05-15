"""
docx-parser — простой HTTP-сервис для извлечения текста из DOCX.
Принимает POST /extract с multipart-формой (поле file) — возвращает {"text": "..."}.
"""
import io
import logging
from flask import Flask, request, jsonify
from docx import Document

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

app = Flask(__name__)


@app.get('/')
def health():
    return jsonify({"status": "ok", "service": "docx-parser"})


@app.get('/health')
def health_check():
    return jsonify({"status": "ok"})


@app.post('/extract')
def extract():
    """
    Принимает DOCX-файл (поле 'file' в multipart-form ИЛИ raw body),
    возвращает извлечённый текст.
    """
    try:
        # Вариант 1: multipart form-data с полем 'file'
        if 'file' in request.files:
            file = request.files['file']
            data = file.read()
        # Вариант 2: raw body (application/octet-stream)
        elif request.data:
            data = request.data
        else:
            return jsonify({"error": "No file provided"}), 400

        if not data:
            return jsonify({"error": "Empty file"}), 400

        doc = Document(io.BytesIO(data))

        # Все параграфы + текст в таблицах
        parts = []
        for p in doc.paragraphs:
            if p.text.strip():
                parts.append(p.text)

        for table in doc.tables:
            for row in table.rows:
                row_text = ' | '.join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    parts.append(row_text)

        text = '\n'.join(parts)
        log.info(f"Extracted {len(text)} chars from {len(data)} byte docx")

        return jsonify({
            "text": text,
            "chars": len(text),
            "paragraphs": len(doc.paragraphs),
            "tables": len(doc.tables)
        })

    except Exception as e:
        log.error(f"Extract error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082, debug=False)
