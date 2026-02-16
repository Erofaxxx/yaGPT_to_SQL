#!/usr/bin/env python3
"""
Yandex GPT to ClickHouse SQL Generator

This program takes a user's natural language request and uses Yandex GPT
to generate an SQL query for ClickHouse database with Yandex Metrika data.
"""

import os
import requests
import json
from typing import Dict, List, Optional


class ClickHouseTableSchema:
    """Represents the schema of a ClickHouse table."""

    def __init__(self, database: str, table: str, columns: Dict[str, str], description: str = ""):
        """
        Initialize table schema.

        Args:
            database: Name of the ClickHouse database
            table: Name of the table
            columns: Dictionary mapping column names to their descriptions
            description: Optional table description
        """
        self.database = database
        self.table = table
        self.columns = columns
        self.description = description

    def get_context_string(self) -> str:
        """Generate a context string for the AI prompt."""
        context = f"База данных: {self.database}\n"
        context += f"Таблица: {self.table}\n"
        if self.description:
            context += f"Описание таблицы: {self.description}\n"
        context += "\nСтолбцы и их описания:\n"
        for col_name, col_desc in self.columns.items():
            context += f"  - {col_name}: {col_desc}\n"
        return context


class YandexGPTSQLGenerator:
    """Generator for SQL queries using Yandex GPT API."""

    def __init__(self, api_key: str, folder_id: str, model: str = "yandexgpt-lite"):
        """
        Initialize the SQL generator.

        Args:
            api_key: Yandex Cloud API key
            folder_id: Yandex Cloud folder ID
            model: Model to use (default: yandexgpt-lite)
        """
        self.api_key = api_key
        self.folder_id = folder_id
        self.model = model
        self.api_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    def generate_sql(
        self,
        user_request: str,
        table_schema: ClickHouseTableSchema,
        temperature: float = 0.3,
        max_tokens: int = 500
    ) -> str:
        """
        Generate SQL query based on user request and table schema.

        Args:
            user_request: Natural language request from user
            table_schema: ClickHouse table schema
            temperature: Model temperature (0.0-1.0)
            max_tokens: Maximum tokens in response

        Returns:
            Generated SQL query as string

        Raises:
            Exception: If API request fails
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self.api_key}"
        }

        # Build system prompt with table context
        system_prompt = self._build_system_prompt(table_schema)

        # Build user prompt
        user_prompt = self._build_user_prompt(user_request, table_schema)

        payload = {
            "modelUri": f"gpt://{self.folder_id}/{self.model}",
            "completionOptions": {
                "temperature": temperature,
                "maxTokens": str(max_tokens)
            },
            "messages": [
                {
                    "role": "system",
                    "text": system_prompt
                },
                {
                    "role": "user",
                    "text": user_prompt
                }
            ]
        }

        response = requests.post(self.api_url, headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()
            sql_query = result["result"]["alternatives"][0]["message"]["text"]
            return sql_query.strip()
        else:
            raise Exception(f"Ошибка API Yandex GPT: {response.status_code}, {response.text}")

    def _build_system_prompt(self, table_schema: ClickHouseTableSchema) -> str:
        """Build system prompt for the AI."""
        return """Ты эксперт по ClickHouse SQL и Яндекс Метрике.
Твоя задача - генерировать оптимальные SQL запросы к ClickHouse на основе запросов пользователя.

Важные правила:
1. Пиши производительные запросы с учетом движков таблиц и партиционирования
2. Используй агрегатные функции ClickHouse когда это уместно
3. Помни, что результаты могут быть далее обработаны в Python, поэтому не обязательно делать всю логику в SQL
4. Возвращай только SQL запрос без дополнительных объяснений
5. Используй корректный синтаксис ClickHouse
6. Учитывай структуру данных Яндекс Метрики"""

    def _build_user_prompt(self, user_request: str, table_schema: ClickHouseTableSchema) -> str:
        """Build user prompt with context."""
        context = table_schema.get_context_string()
        return f"""{context}

Запрос пользователя: {user_request}

Сгенерируй SQL запрос к ClickHouse, который поможет получить данные для ответа на этот запрос.
Верни только SQL запрос без дополнительных объяснений."""


def create_default_metrika_schema() -> ClickHouseTableSchema:
    """
    Create a default schema for Yandex Metrika data in ClickHouse.
    This is an example - adjust according to your actual table structure.
    """
    columns = {
        "EventDate": "Дата события (Date)",
        "EventDateTime": "Дата и время события (DateTime)",
        "CounterID": "ID счетчика Метрики (UInt32)",
        "UserID": "Анонимный ID пользователя (UInt64)",
        "SessionID": "ID сессии (UInt64)",
        "ClientIP": "IP адрес пользователя (UInt32)",
        "RegionID": "ID региона пользователя (UInt32)",
        "CountryID": "ID страны пользователя (UInt16)",
        "URL": "URL страницы (String)",
        "Referer": "Реферер (String)",
        "Title": "Заголовок страницы (String)",
        "UTMSource": "UTM источник (String)",
        "UTMMedium": "UTM medium (String)",
        "UTMCampaign": "UTM кампания (String)",
        "UTMContent": "UTM content (String)",
        "UTMTerm": "UTM term (String)",
        "DeviceCategory": "Категория устройства (mobile/tablet/desktop) (String)",
        "MobilePhone": "Модель мобильного телефона (String)",
        "MobilePhoneModel": "Модель мобильного устройства (String)",
        "Browser": "Браузер (String)",
        "BrowserVersion": "Версия браузера (String)",
        "OS": "Операционная система (String)",
        "Age": "Возраст пользователя (UInt8)",
        "Sex": "Пол пользователя (0-женский, 1-мужской) (UInt8)",
        "Goals.ID": "Массив ID достигнутых целей (Array(UInt32))",
        "Goals.DateTime": "Массив времен достижения целей (Array(DateTime))",
        "PageViews": "Количество просмотров страниц в сессии (UInt32)",
        "Duration": "Длительность сессии в секундах (UInt32)",
        "Bounce": "Отказ (1-да, 0-нет) (UInt8)",
        "IsNewUser": "Новый пользователь (1-да, 0-нет) (UInt8)"
    }

    return ClickHouseTableSchema(
        database="metrika",
        table="hits",
        columns=columns,
        description="Таблица с данными о хитах (просмотрах страниц) из Яндекс Метрики"
    )


def main():
    """Main function for interactive usage."""
    print("=== Yandex GPT to ClickHouse SQL Generator ===\n")

    # Get credentials from environment variables
    api_key = os.getenv("YANDEX_API_KEY")
    folder_id = os.getenv("YANDEX_FOLDER_ID")

    if not api_key or not folder_id:
        print("Ошибка: Необходимо установить переменные окружения:")
        print("  YANDEX_API_KEY - API ключ Yandex Cloud")
        print("  YANDEX_FOLDER_ID - ID каталога Yandex Cloud")
        print("\nПример:")
        print("  export YANDEX_API_KEY='your_api_key'")
        print("  export YANDEX_FOLDER_ID='your_folder_id'")
        return

    # Initialize generator with default Metrika schema
    schema = create_default_metrika_schema()
    generator = YandexGPTSQLGenerator(api_key, folder_id)

    print(f"Используется схема: {schema.database}.{schema.table}")
    print(f"Количество столбцов: {len(schema.columns)}\n")

    # Interactive loop
    print("Введите ваш запрос (или 'exit' для выхода):\n")

    while True:
        user_input = input("Запрос> ").strip()

        if user_input.lower() in ['exit', 'quit', 'выход']:
            print("До свидания!")
            break

        if not user_input:
            continue

        try:
            print("\nГенерирую SQL запрос...")
            sql_query = generator.generate_sql(user_input, schema)
            print("\n--- Сгенерированный SQL запрос ---")
            print(sql_query)
            print("-----------------------------------\n")
        except Exception as e:
            print(f"\nОшибка: {e}\n")


if __name__ == "__main__":
    main()
