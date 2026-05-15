# docx-parser

Маленький HTTP-сервис для извлечения текста из `.docx` файлов. Сделан для использования с n8n (или любой другой автоматизацией) — принимает POST с файлом, возвращает JSON с текстом.

## Эндпоинты

- `GET /health` — проверка живости, возвращает `{"status": "ok"}`.
- `POST /extract` — принимает DOCX, возвращает текст.

### Пример запроса

```bash
curl -X POST -F "file=@card.docx" http://localhost:8082/extract
```

Альтернатива — отправить файл как raw body:

```bash
curl -X POST --data-binary @card.docx \
  -H "Content-Type: application/octet-stream" \
  http://localhost:8082/extract
```

### Пример ответа

```json
{
  "text": "ООО «Кендалл»\nИНН 5009134368\nКПП 500901001\n...",
  "chars": 1234,
  "paragraphs": 25,
  "tables": 1
}
```

В случае ошибки:

```json
{"error": "описание"}
```

(HTTP 400 для проблем с файлом, 500 — внутренние ошибки.)

## Локальный запуск

```bash
pip install -r requirements.txt
python app.py
```

Сервис стартует на `http://0.0.0.0:8082`.

## Docker

```bash
docker build -t docx-parser .
docker run -d --name docx-parser -p 8082:8082 --restart unless-stopped docx-parser
```

## Деплой в Coolify (через GitHub)

1. Создайте репозиторий на GitHub и положите туда содержимое этой папки.

2. В Coolify откройте проект, где живёт n8n → **+ New Resource** → **Public Repository** (или **Private Repository** + Deploy Key).

3. Заполните:
   - **Repository URL** — ваш GitHub URL.
   - **Branch** — `main` (или `master`).
   - **Build Pack** — **Dockerfile**.
   - **Port (exposed)** — `8082`.

4. **Important — Network:** чтобы n8n мог достучаться до сервиса по имени `docx-parser`, оба контейнера должны быть в одной Docker-сети.
   - Создайте сервис в **том же Coolify-проекте**, что n8n — Coolify их сам поместит в общую сеть проекта.
   - В настройках сервиса убедитесь, что **Container Name** = `docx-parser` (это имя, по которому n8n будет обращаться).

5. **Deploy.** Coolify соберёт образ из Dockerfile и запустит контейнер.

6. **Проверка из n8n:** в Terminal контейнера n8n:

   ```bash
   wget -O- http://docx-parser:8082/health
   ```

   Должно вернуть `{"status": "ok"}`.

7. **Проверка с хоста:**

   ```bash
   curl http://localhost:8082/health
   ```

   (Coolify по умолчанию мапит порт на хост.)

## Использование из n8n

В HTTP Request ноде:

| Поле | Значение |
|------|----------|
| Method | `POST` |
| URL | `http://docx-parser:8082/extract` |
| Send Body | ✅ |
| Body Content Type | `Form-Data Multipart` |
| Body Parameters | `file` (Binary Data) ← из предыдущей ноды |

Ответ:

```json
{ "text": "..." }
```

Текст в JSON-ответе доступен как `$json.text`.

## Лимиты и производительность

- В Dockerfile используется gunicorn с 2 воркерами × 4 потока — хватает на ~8 параллельных запросов.
- Timeout одного запроса — 120 секунд (для крупных DOCX).
- Максимальный размер файла — по умолчанию неограниченно, ограничивайте на стороне n8n или nginx.
- Чистая память ~80 MB.

## Безопасность

⚠️ Сервис не имеет аутентификации. Если контейнер торчит в интернет — закройте его за reverse-proxy с Basic Auth, или ограничьте доступ только из сети Coolify.

В нашей конфигурации он живёт **внутри Docker-сети** и не выставлен наружу — это безопасно.

## Стек

- Python 3.12
- Flask 3.0
- python-docx 1.1
- gunicorn 23.0

## Лицензия

MIT.
