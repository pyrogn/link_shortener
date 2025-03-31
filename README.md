# Link Shortener

Простой сервис для сокращения длинных URL-адресов.

## Описание API

| Эндпоинт | Метод | Описание |
|----------|--------|-------------|
| `/links/shorten` | POST | Создать новую короткую ссылку |
| `/{short_code}` | GET | Перенаправить на оригинальный URL |
| `/links/{short_code}` | GET | Получить информацию о ссылке и статистику |
| `/links/{short_code}` | PUT | Обновить ссылку |
| `/links/{short_code}` | DELETE | Удалить ссылку |
| `/links/search` | GET | Найти ссылку по оригинальному URL |

## Тестирование

Запуск тестов:

```bash
uv run pytest
```

Проверка coverage:

```bash
uv run coverage run -m pytest
uv run coverage report
```

Или готовый скрипт:

```bash
./run_tests.sh
```

Тесты покрывают все основные функции API.

## Примеры запросов

### Создание короткой ссылки

```bash
curl -X POST "http://localhost:8000/links/shorten" \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://example.com/very/long/url/that/needs/shortening"}'
```

Ответ:
```json
{
  "short_code": "abc123",
  "original_url": "https://example.com/very/long/url/that/needs/shortening",
  "created_at": "2025-03-31T10:30:00",
  "expires_at": null,
  "clicks": 0,
  "last_accessed": null
}
```

Далее в браузере введите `http://localhost:8000/abc123` (код рандомизирован) и вы будете перенаправлены на `https://example.com/very/long/url/that/needs/shortening`.

### Создание короткой ссылки с пользовательским псевдонимом

```bash
curl -X POST "http://localhost:8000/links/shorten" \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://example.com/very/long/url", "custom_alias": "mylink"}'
```

### Создание короткой ссылки с таймаутом

```bash
curl -X POST "http://localhost:8000/links/shorten" \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://example.com/temporary/link", "expires_at": "2025-04-30T23:59:59"}'
```

### Получение статистики ссылки

```bash
curl -X GET "http://localhost:8000/links/abc123"
```

### Обновление ссылки

```bash
curl -X PUT "http://localhost:8000/links/abc123" \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://example.com/updated/url"}'
```

### Удаление ссылки

```bash
curl -X DELETE "http://localhost:8000/links/abc123"
```

### Поиск ссылки по оригинальному URL

```bash
curl -X GET "http://localhost:8000/links/search?original_url=https://example.com/very/long/url"
```

## Как запустить

### Разработка

```bash
uv run fastapi dev
```

### Production

```bash
uv run fastapi run
```

Или Docker:

```bash
docker build -t link-shortener-app .
docker run -p 8000:80 link-shortener-app
```

## Хранение данных

Текущая реализация использует структуры данных в памяти:

- `links_db`: Словарь, сопоставляющий короткие коды с объектами ссылок
- `original_url_index`: Словарь, сопоставляющий оригинальные URL с их короткими кодами

## Что сделано иначе

- Короткую ссылку получаем по GET `/{short_code}` для простоты
- Статистика вынесена в GET `/links/{short_code}`, а не в `/links/{short_code}/stats`

## Что не сделано

- Нет проверки регистрации
- В качестве БД используется словарь в памяти (для простоты)
- А значит и кэширование не требуется, так как все данные хранятся в памяти
