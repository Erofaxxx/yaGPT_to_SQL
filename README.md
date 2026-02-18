# Yandex GPT to ClickHouse SQL Generator

Программа для генерации SQL запросов к ClickHouse с помощью Yandex GPT на основе естественного языка пользователя.

## Описание

Эта программа принимает запрос пользователя на естественном языке и использует Yandex GPT для генерации оптимального SQL запроса к базе данных ClickHouse с данными Яндекс Метрики.

### Основные возможности

- Генерация SQL запросов на основе естественного языка
- Настраиваемая схема таблиц ClickHouse
- Поддержка контекста с описанием столбцов
- Интерактивный режим работы
- Готовая схема для данных Яндекс Метрики

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/Erofaxxx/yaGPT_to_SQL.git
cd yaGPT_to_SQL
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Настройка

Перед использованием необходимо получить API ключ и ID каталога в Yandex Cloud:

1. Зарегистрируйтесь в [Yandex Cloud](https://cloud.yandex.ru/)
2. Создайте API ключ в консоли управления
3. Получите ID каталога (folder_id)

Установите переменные окружения:

```bash
export YANDEX_API_KEY='ваш_api_ключ'
export YANDEX_FOLDER_ID='ваш_folder_id'
```

Или создайте файл `.env`:
```
YANDEX_API_KEY=ваш_api_ключ
YANDEX_FOLDER_ID=ваш_folder_id
```

## Использование

### Интерактивный режим

Запустите программу в интерактивном режиме:

```bash
python yagpt_to_sql.py
```

Введите ваш запрос на естественном языке:
```
Запрос> Найди топ-5 самых активных пользователей по количеству событий за последние 7 дней
```

Программа вернет SQL запрос для ClickHouse.

### Программное использование

```python
from yagpt_to_sql import YandexGPTSQLGenerator, create_default_metrika_schema

# Инициализация
api_key = "ваш_api_ключ"
folder_id = "ваш_folder_id"

schema = create_default_metrika_schema()
generator = YandexGPTSQLGenerator(api_key, folder_id)

# Генерация SQL
user_request = "Покажи количество сессий по странам за вчера"
sql_query = generator.generate_sql(user_request, schema)
print(sql_query)
```

### Настройка собственной схемы

Вы можете создать собственную схему таблицы:

```python
from yagpt_to_sql import ClickHouseTableSchema, YandexGPTSQLGenerator

# Определите структуру вашей таблицы
columns = {
    "event_date": "Дата события (Date)",
    "user_id": "ID пользователя (UInt64)",
    "event_type": "Тип события (String)",
    "value": "Значение события (Float64)"
}

schema = ClickHouseTableSchema(
    database="my_database",
    table="events",
    columns=columns,
    description="Таблица событий пользователей"
)

# Используйте схему для генерации
generator = YandexGPTSQLGenerator(api_key, folder_id)
sql = generator.generate_sql("Найди среднее значение по типам событий", schema)
```

## Примеры запросов

### Пример 1: Агрегация по странам
```
Запрос: Покажи количество пользователей по странам за последний месяц
```

### Пример 2: Временной анализ
```
Запрос: Сгруппируй сессии по часам дня и покажи среднюю длительность
```

### Пример 3: Фильтрация и сортировка
```
Запрос: Найди топ-10 страниц с самым большим количеством отказов
```

### Пример 4: Мобильные устройства
```
Запрос: Посчитай долю мобильного трафика от общего за вчера
```

## Структура проекта

```
yaGPT_to_SQL/
├── yagpt_to_sql.py      # Основной модуль программы
├── requirements.txt      # Зависимости Python
├── README.md            # Документация
└── промпты.txt          # Исходное задание
```

## Технические детали

### Классы

- **ClickHouseTableSchema**: Хранит информацию о структуре таблицы ClickHouse
- **YandexGPTSQLGenerator**: Основной класс для генерации SQL через Yandex GPT API

### Параметры генерации

- `temperature` (по умолчанию 0.3): Контролирует креативность модели (0.0-1.0)
- `max_tokens` (по умолчанию 500): Максимальная длина ответа
- `model` (по умолчанию "yandexgpt-lite"): Модель Yandex GPT

## Документация

- [Yandex GPT API](https://cloud.yandex.ru/docs/yandexgpt/)
- [ClickHouse Python Driver](https://clickhouse.com/docs/integrations/python)
- [Яндекс Метрика](https://metrika.yandex.ru/)
- [ClickHouse System Tables Guide](SYSTEM_TABLES_GUIDE.md) - Руководство по работе с системными таблицами ClickHouse

## Известные проблемы и решения

### Ошибка синтаксиса при запросе к системным таблицам

Если вы получаете ошибку вида:
```
Syntax error: failed at position 65 (WHERE) (line 6, col 1): WHERE table = 'visits_complete'
```

Это означает, что сгенерирован неправильный запрос к системной таблице. Обновленная версия программы включает исправления для корректной генерации таких запросов. См. [SYSTEM_TABLES_GUIDE.md](SYSTEM_TABLES_GUIDE.md) для деталей.

## Лицензия

MIT

## Автор

Erofaxxx
