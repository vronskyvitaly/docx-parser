# docx-parser

Лёгкий HTTP-микросервис для работы с документами Word в пайплайне таможенного брокера. Принимает DOCX-файлы с реквизитами клиентов, извлекает текст для дальнейшего парсинга ИИ, а также генерирует готовые договоры (PDF и DOCX) по шаблону с реквизитами компании.

Разворачивается в Docker, деплоится через Coolify — автоматически при пуше в `main`.

---

## Возможности

| Эндпоинт | Метод | Что делает |
|---|---|---|
| `/health` | GET | Проверка живости сервиса |
| `/extract` | POST | Извлекает текст из DOCX, возвращает JSON |
| `/generate-contract` | POST | Рендерит договор по шаблону → возвращает PDF |
| `/generate-contract-docx` | POST | То же самое → возвращает DOCX |

---

## Быстрый старт

### Локально

```bash
pip install -r requirements.txt
python app.py
# Сервис доступен на http://localhost:8082
```

### Docker

```bash
docker build -t docx-parser .
docker run -d -p 8082:8082 --restart unless-stopped docx-parser
```

---

## API

### POST /extract

Принимает DOCX-файл, возвращает извлечённый текст.

```bash
curl -X POST -F "file=@card.docx" http://localhost:8082/extract
```

Или как raw body:

```bash
curl -X POST --data-binary @card.docx \
  -H "Content-Type: application/octet-stream" \
  http://localhost:8082/extract
```

**Ответ:**

```json
{
  "text": "ООО «Омега»\nИНН 7718100830\nКПП 772001001\n...",
  "chars": 1234,
  "paragraphs": 25,
  "tables": 1
}
```

---

### POST /generate-contract

Рендерит договор на оказание услуг таможенного представителя по шаблону `templates/contract.docx`.

**Запрос (JSON):**

```json
{
  "contract_number": "415",
  "contract_date": "26.06.2026",
  "client": {
    "company_name": "ООО «Омега»",
    "inn": "7718100830",
    "kpp": "772001001",
    "ogrn": "1157746208729",
    "address": "111123, Москва, ш. Энтузиастов, д. 31",
    "account": "40702810413000010925",
    "bank": "ПАО Сбербанк",
    "bik": "042007681",
    "cor_account": "30101810600000000681",
    "director_genitive": "Елютина Ивана Михайловича",
    "director_short": "Елютин И.М.",
    "intro_clause": ", в лице генерального директора Елютина Ивана Михайловича, действующего на основании Устава",
    "email": "client@example.com",
    "phone": "+7 903 030 99 94"
  }
}
```

**Ответ:** бинарный PDF (`application/pdf`) с именем `Contract_415.pdf`.

Эндпоинт `/generate-contract-docx` принимает тот же JSON, возвращает `.docx`.

---

## Реквизиты компании

Реквизиты Представителя задаются через переменные окружения в Coolify — не хардкодятся в образе:

| Переменная | Описание |
|---|---|
| `ROYAL_NAME` | Название компании |
| `ROYAL_INN` | ИНН |
| `ROYAL_KPP` | КПП |
| `ROYAL_OGRN` | ОГРН |
| `ROYAL_ADDRESS` | Юридический адрес |
| `ROYAL_ACCOUNT` | Расчётный счёт |
| `ROYAL_BANK` | Банк |
| `ROYAL_BIK` | БИК |
| `ROYAL_COR_ACCOUNT` | Корр. счёт |
| `ROYAL_DIRECTOR_GEN` | ФИО директора в род. падеже |
| `ROYAL_DIRECTOR_SHORT` | ФИО кратко (Фамилия И.О.) |
| `ROYAL_EMAIL` | Email компании |
| `ROYAL_PHONE` | Телефон (п. 2.4.1 договора) |

---

## Деплой в Coolify

1. Подключите репозиторий в Coolify → **Build Pack: Dockerfile**.
2. Укажите **Port: 8082**.
3. Заполните переменные окружения (реквизиты компании).
4. Нажмите **Deploy** — при каждом пуше в `main` Coolify пересобирает образ автоматически.

**Проверка после деплоя:**

```bash
curl https://parser.yourdomain.ru/health
# {"status": "ok"}
```

---

## Стек

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask)
![Docker](https://img.shields.io/badge/Docker-Dockerfile-2496ED?logo=docker&logoColor=white)
![LibreOffice](https://img.shields.io/badge/LibreOffice-headless-18A303?logo=libreoffice)
![Coolify](https://img.shields.io/badge/Coolify-self--hosted-7C3AED)

- **Flask 3.0** — HTTP-сервер
- **python-docx** — извлечение текста из DOCX
- **docxtpl** — рендеринг договора по Jinja2-шаблону
- **LibreOffice headless** — конвертация DOCX → PDF
- **gunicorn** — production WSGI-сервер (2 воркера × 4 потока)

---

## Безопасность

Сервис не имеет аутентификации — он живёт внутри закрытой Docker-сети Coolify и не выставлен напрямую в интернет. Если вы открываете порт наружу — закройте его Basic Auth на уровне reverse-proxy.

---

## Лицензия

MIT
