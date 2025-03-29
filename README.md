# Todo API с поддержкой тегов

API для управления задачами (Todo) с возможностью добавления тегов.

## Функциональность

- Создание, чтение, обновление и удаление задач
- Создание, чтение, обновление и удаление тегов
- Пагинация и фильтрация задач
- Валидация входных данных

## Технический стек

- Python 3.10+
- FastAPI 0.95+
- MongoDB (через Motor для асинхронной работы)
- Pydantic 2.0+

## Установка и запуск

1. Клонировать репозиторий
2. Создать виртуальное окружение:
   ```
   python -m venv venv
   source venv/bin/activate  # для Linux/macOS
   venv\Scripts\activate     # для Windows
   ```
3. Установить зависимости:
   ```
   pip install -r requirements.txt
   ```
4. Создать файл `.env` на основе `.env.example`
5. Запустить MongoDB
6. Запустить приложение:
   ```
   python main.py
   ```

После запуска API будет доступно по адресу http://localhost:8000

## API Endpoints

### Задачи (Todo)

- `GET /api/todos` - Получить список задач
- `GET /api/todos/{todo_id}` - Получить задачу по ID
- `POST /api/todos` - Создать новую задачу
- `PUT /api/todos/{todo_id}` - Обновить задачу
- `DELETE /api/todos/{todo_id}` - Удалить задачу

### Теги (Tags)

- `GET /api/tags` - Получить список тегов
- `GET /api/tags/{tag_id}` - Получить тег по ID
- `POST /api/tags` - Создать новый тег
- `PUT /api/tags/{tag_id}` - Обновить тег
- `DELETE /api/tags/{tag_id}` - Удалить тег

## Примеры запросов

### Создание тега

```
POST /api/tags
{
  "name": "Важное",
  "color": "#ff0000"
}
```

### Создание задачи с тегами

```
POST /api/todos
{
  "title": "Изучить FastAPI",
  "description": "Изучить основы FastAPI и создать проект",
  "due_date": "2023-12-31T00:00:00",
  "tags": ["идентификатор_тега_1", "идентификатор_тега_2"]
}
```

### Получение списка задач с фильтрацией

```
GET /api/todos?is_completed=false&tag_id=идентификатор_тега
```

### Пагинация

```
GET /api/todos?limit=5&offset=10
```
