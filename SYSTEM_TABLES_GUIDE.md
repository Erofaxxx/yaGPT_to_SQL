# ClickHouse System Tables Query Examples

This document provides examples of correct ClickHouse system table queries that the Yandex GPT SQL generator should produce.

## Common Issue

The error shown in the problem statement:
```
SELECT name, type FROM ym_sanok.system.columns WHERE table = 'visits_complete'
```

This is **INCORRECT** syntax. System tables are not within user databases.

## Correct Syntax

### Query Table Columns

**Correct:**
```sql
SELECT name, type FROM system.columns WHERE database = 'ym_sanok' AND table = 'visits_complete'
```

With JSON format:
```sql
SELECT name, type FROM system.columns WHERE database = 'ym_sanok' AND table = 'visits_complete' FORMAT JSON
```

### Query All Tables in a Database

```sql
SELECT name FROM system.tables WHERE database = 'ym_sanok'
```

### Query All Databases

```sql
SELECT name FROM system.databases
```

### Query Table Engine Information

```sql
SELECT name, engine FROM system.tables WHERE database = 'ym_sanok' AND name = 'visits_complete'
```

### Query Column Details

```sql
SELECT
    name,
    type,
    default_kind,
    default_expression,
    comment
FROM system.columns
WHERE database = 'ym_sanok' AND table = 'visits_complete'
ORDER BY position
```

## Key Points

1. **System tables are in the `system` database**, not in user databases
2. **Use `database = 'name'` in WHERE clause**, not just `table = 'name'`
3. **FORMAT clause goes at the end** of the query
4. The AI should return **clean SQL without markdown** code blocks (no ``` markers)

## Examples for Testing

After the fix, these user requests should generate correct queries:

1. "Выведи названия столбцов и типы данных из этих столбцов"
   - Should generate: `SELECT name, type FROM system.columns WHERE database = 'ym_sanok' AND table = 'visits_complete'`

2. "Покажи все таблицы в базе данных"
   - Should generate: `SELECT name FROM system.tables WHERE database = 'ym_sanok'`

3. "Какой движок использует таблица visits_complete?"
   - Should generate: `SELECT engine FROM system.tables WHERE database = 'ym_sanok' AND name = 'visits_complete'`

## What Was Fixed

1. **Updated system prompt** to explicitly teach the correct syntax for system table queries
2. **Added SQL cleaning function** to remove markdown formatting (```sql and ```)
3. **Provided clear examples** in the AI prompt of correct vs incorrect syntax
4. **Added FORMAT clause guidance** to place it at the end of queries
