# yaGPT to SQL

Программа для генерации SQL запросов к ClickHouse с использованием Yandex GPT.

## Описание

Эта программа принимает запросы пользователя на естественном языке и генерирует SQL запросы для ClickHouse, используя Yandex GPT API. Программа автоматически получает информацию о структуре таблицы и передает её в контекст модели для более точной генерации запросов.

## Возможности

- 🤖 Генерация SQL запросов с использованием Yandex GPT 5.1
- 📊 Автоматическое получение структуры таблицы из ClickHouse
- 🔍 Контекстная генерация с учётом типов данных и описаний столбцов
- ⚡ Поддержка работы с данными из Яндекс Метрики
- 🛠️ Возможность выполнения сгенерированных запросов

## Требования

- Python 3.7+
- Доступ к Yandex Cloud API (API ключ и folder ID)
- Доступ к ClickHouse базе данных

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

3. Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

4. Заполните файл `.env` вашими данными:
```
YANDEX_API_KEY=ваш_api_ключ
YANDEX_FOLDER_ID=ваш_folder_id
CLICKHOUSE_HOST=адрес_clickhouse
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER=пользователь
CLICKHOUSE_PASSWORD=пароль
CLICKHOUSE_DATABASE=база_данных
CLICKHOUSE_TABLE=название_таблицы
```

## Использование

### Запуск программы

```bash
python yagpt_to_sql.py
```

Программа запросит ваш запрос на естественном языке или использует пример по умолчанию.

### Примеры запросов

1. **Топ пользователей**:
   ```
   Напиши запрос, который найдёт топ-5 самых активных пользователей по количеству событий за последние 7 дней, с группировкой по стране.
   ```

2. **Анализ сессий**:
   ```
   Составь запрос, который агрегирует данные по сессиям пользователей за вчера, с фильтрацией по мобильным устройствам и сортировкой по длительности.
   ```

3. **Статистика по источникам**:
   ```
   Выведи статистику по источникам трафика за последний месяц с группировкой по дням.
   ```

### Использование как библиотеки

```python
from yagpt_to_sql import YandexGPTSQLGenerator, ClickHouseHelper

# Инициализация генератора SQL
sql_generator = YandexGPTSQLGenerator(
    api_key="ваш_api_ключ",
    folder_id="ваш_folder_id"
)

# Инициализация помощника ClickHouse
ch_helper = ClickHouseHelper(
    host="localhost",
    port=8123,
    user="default",
    password="",
    database="default"
)

# Получение информации о таблице
table_info = ch_helper.get_table_info("metrika_hits")

# Генерация SQL запроса
user_request = "Найди топ-10 страниц по количеству просмотров за сегодня"
sql_query = sql_generator.generate_sql(user_request, table_info)

print(sql_query)

# Выполнение запроса (опционально)
results = ch_helper.execute_query(sql_query)
```

## Настройка

### Переменные окружения

- `YANDEX_API_KEY` - API ключ Yandex Cloud
- `YANDEX_FOLDER_ID` - ID каталога в Yandex Cloud
- `CLICKHOUSE_HOST` - Адрес сервера ClickHouse
- `CLICKHOUSE_PORT` - Порт ClickHouse (по умолчанию 8123)
- `CLICKHOUSE_USER` - Имя пользователя ClickHouse
- `CLICKHOUSE_PASSWORD` - Пароль пользователя ClickHouse
- `CLICKHOUSE_DATABASE` - Имя базы данных
- `CLICKHOUSE_TABLE` - Имя таблицы с данными Яндекс Метрики

### Параметры генерации

В методе `generate_sql()` можно настроить:
- `temperature` (0.0-1.0) - контролирует случайность генерации (по умолчанию 0.3)
- `max_tokens` - максимальное количество токенов в ответе (по умолчанию 500)

## Архитектура

Программа состоит из двух основных классов:

### YandexGPTSQLGenerator

Отвечает за взаимодействие с Yandex GPT API:
- Формирует контекст с информацией о таблице
- Отправляет запросы к API
- Обрабатывает ответы и извлекает SQL

### ClickHouseHelper

Отвечает за работу с ClickHouse:
- Получает структуру таблицы (столбцы, типы, описания)
- Выполняет SQL запросы
- Возвращает результаты в удобном формате

## Документация

- [ClickHouse Python интеграция](https://clickhouse.com/docs/integrations/python)
- [Yandex GPT API](https://cloud.yandex.ru/docs/yandexgpt/)
- [Yandex Метрика](https://metrika.yandex.ru/)

## Особенности

- Программа учитывает, что SQL запросы будут использоваться для выгрузки срезов данных с последующей обработкой в Python
- Не обязательно полностью вычислять всё в SQL - некоторые анализы проще делать в Python
- Генератор оптимизирован для работы с данными Яндекс Метрики

## Лицензия

MIT

## Автор

Erofaxxx
