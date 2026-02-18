# Анализ рекомендаций Yandex WebSQL Concierge

## Источник: Yandex_assistant_prompt.txt

### Проблема, которую решали

Пользователь получал **некорректные SQL-запросы** от Yandex GPT для ClickHouse:

```sql
❌ НЕПРАВИЛЬНО (генерировалось):
SELECT arrayJoin(map(x -> x.name, x -> x.type, groupArray(system.columns))) AS columns
FROM system.columns
WHERE database = 'ym_sanok' AND table = 'visits_complete'
FORMAT JSON
```

**Ошибка**: `Syntax error: failed at position 37 (->)`

### Почему это не работало?

1. **Некорректный синтаксис ClickHouse**:
   - `map(x -> x.name, x -> x.type, ...)` - неправильное использование lambda-функций
   - `groupArray(system.columns)` - нельзя группировать строки таким образом
   - Lambda-функции в ClickHouse используются иначе

2. **Излишняя сложность**:
   - Для простого запроса "показать столбцы" использовались продвинутые функции
   - Нет необходимости в arrayJoin и map для получения списка столбцов

### Правильное решение от Yandex WebSQL Concierge

```sql
✅ ПРАВИЛЬНО:
SELECT name, type 
FROM system.columns
WHERE database = 'ym_sanok' AND table = 'visits_complete'
ORDER BY position
```

Или с JSON форматом:
```sql
SELECT name, type 
FROM system.columns
WHERE database = 'ym_sanok' AND table = 'visits_complete'
ORDER BY position
FORMAT JSON
```

### Ключевые рекомендации от Yandex Assistant

#### 1. Контекст базы данных в JSON формате

Yandex assistant рекомендует передавать контекст в структурированном JSON:

```json
{
  "databaseType": "clickhouse",
  "databaseName": "ym_sanok",
  "tables": [
    {
      "name": "visits_complete",
      "columns": [
        { "name": "ClientID", "type": "UInt64" },
        { "name": "StartDate", "type": "Date" }
      ]
    }
  ]
}
```

#### 2. Использовать полную модель YandexGPT

Цитата из файла (строки 310-315):
> "Вы можете использовать:
> - Yandex AI API — например, YandexGPT или Embeddings
> - Интегрировать их в свой бэкенд
> - Обучить модель на документации ClickHouse и шаблонах SQL"

**Рекомендация**: Использовать `yandexgpt` (полная модель), а не `yandexgpt-lite`

#### 3. Явно указывать особенности ClickHouse

Из строк 68-74:
> "Мои знания о ClickHouse основаны на:
> - Официальной документации ClickHouse
> - Практических примерах использования
> - Особенностях синтаксиса, функций (arrayJoin, groupArray, map, FORMAT, system.* таблицы и т.д.)
> - Лучших практиках производительности и безопасности"

#### 4. Конкретные примеры в промпте

Yandex assistant показал, что нужны **конкретные примеры** правильных запросов, а не просто описание возможностей.

### Что было реализовано

#### ✅ Изменение 1: Добавлена поддержка выбора модели

```python
# В .env.example
YANDEX_GPT_MODEL=yandexgpt  # вместо жёстко закодированного yandexgpt-lite

# В коде
def __init__(self, api_key: str, folder_id: str, model: str = "yandexgpt-lite"):
    self.model = model
```

#### ✅ Изменение 2: Контекст в JSON формате (как рекомендовал assistant)

```python
context = f"""Ты — SQL-эксперт для ClickHouse. Твоя задача — генерировать правильные, простые и эффективные SQL-запросы.

КОНТЕКСТ БАЗЫ ДАННЫХ (JSON):
{{
  "databaseType": "clickhouse",
  "databaseName": "{database}",
  "tableName": "{table}",
  "columns": [
    {{"name": "col1", "type": "Type1"}},
    ...
  ]
}}
```

#### ✅ Изменение 3: Раздел "ЗАПРЕЩЕННЫЕ конструкции"

Явно указываем ошибочные паттерны из Yandex_assistant_prompt.txt:

```
ЗАПРЕЩЕННЫЕ конструкции (генерируют ОШИБКИ):
❌ arrayJoin(map(x -> x.name, ...)) - некорректный синтаксис!
❌ groupArray(system.columns) - нельзя группировать строки так!
❌ map(x -> x.name, x -> x.type, ...) - неправильное использование map()!
```

#### ✅ Изменение 4: Примеры правильных запросов

Добавлены конкретные примеры из рекомендаций assistant:

```
1. Список столбцов таблицы:
   SELECT name, type 
   FROM system.columns 
   WHERE database = 'db' AND table = 'table'
   ORDER BY position
   FORMAT JSON
```

#### ✅ Изменение 5: Принципы генерации

```
ПРИНЦИПЫ ГЕНЕРАЦИИ:
1. ПРОСТОТА: используй базовый SELECT/WHERE/GROUP BY
2. FORMAT JSON: ОБЯЗАТЕЛЬНО добавляй в конец каждого SELECT
3. НЕ УСЛОЖНЯЙ: избегай lambda-функций без необходимости
4. ПРОВЕРЯЙ: используй только существующие столбцы из контекста
5. ЧИТАЕМОСТЬ: пиши SQL, который легко понять
```

### Ожидаемый результат

После этих изменений, при запросе "Выведи названия столбцов и типы данных":

**РАНЬШЕ** (с yandexgpt-lite, без структурированного контекста):
```sql
❌ SELECT arrayJoin(map(x -> x.name, x -> x.type, groupArray(system.columns)))...
   Ошибка синтаксиса!
```

**ТЕПЕРЬ** (с yandexgpt, со структурированным контекстом и примерами):
```sql
✅ SELECT name, type 
   FROM system.columns 
   WHERE database = 'ym_sanok' AND table = 'visits_complete'
   FORMAT JSON
   
   Работает корректно!
```

### Как использовать

1. Обновите `.env`:
   ```bash
   YANDEX_GPT_MODEL=yandexgpt  # полная модель, не lite
   ```

2. Убедитесь, что есть API ключ с доступом к полной модели

3. Запустите программу:
   ```bash
   python yagpt_to_sql.py
   ```

### Итоговая оценка

| Критерий | До изменений | После изменений |
|----------|-------------|-----------------|
| Модель | yandexgpt-lite (жёстко) | Настраиваемая (рекомендуется yandexgpt) |
| Формат контекста | Текстовый список | JSON (как рекомендовал Yandex assistant) |
| Примеры запросов | Общие описания | Конкретные примеры SQL |
| Запрещённые паттерны | Не указаны | Явно перечислены с примерами |
| Принципы | Размыты в тексте | Четкий пронумерованный список |

### Выводы

Yandex WebSQL Concierge дал **конкретные рекомендации**, которые мы реализовали:

1. ✅ JSON-формат контекста
2. ✅ Явные примеры правильных запросов
3. ✅ Список запрещённых конструкций
4. ✅ Использование полной модели YandexGPT
5. ✅ Простота как основной принцип

Эти изменения должны значительно улучшить качество генерируемых SQL-запросов.
