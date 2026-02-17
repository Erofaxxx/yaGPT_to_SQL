"""
yaGPT to SQL - Program for generating ClickHouse SQL queries using Yandex GPT
"""

import os
import requests
from typing import Dict, List, Optional, Any
import json


class YandexGPTSQLGenerator:
    """Class for generating ClickHouse SQL queries using Yandex GPT"""
    
    def __init__(self, api_key: str, folder_id: str):
        """
        Initialize the SQL generator
        
        Args:
            api_key: Yandex Cloud API key
            folder_id: Yandex Cloud folder ID
        """
        self.api_key = api_key
        self.folder_id = folder_id
        self.api_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    
    def build_context(self, table_info: Dict[str, Any]) -> str:
        """
        Build context message with table information
        
        Args:
            table_info: Dictionary with table information (database, table, columns, description)
            
        Returns:
            Formatted context string
        """
        context = f"""Ты эксперт по ClickHouse SQL. Пиши оптимальные, производительные запросы с учетом движков таблиц и партиционирования.

Информация о таблице:
- База данных: {table_info.get('database', 'default')}
- Таблица: {table_info.get('table', 'unknown')}
- Описание: {table_info.get('description', 'Таблица содержит данные из Яндекс Метрики')}

Структура таблицы:
"""
        
        columns = table_info.get('columns', [])
        if columns:
            for col in columns:
                col_name = col.get('name', '')
                col_type = col.get('type', '')
                col_desc = col.get('description', '')
                context += f"\n- {col_name} ({col_type})"
                if col_desc:
                    context += f": {col_desc}"
        else:
            context += "\n(Информация о столбцах недоступна)"
        
        context += "\n\nУчитывай, что SQL запрос будет использоваться для выгрузки среза данных, которые затем будут обрабатываться Python кодом. Не обязательно полностью всё вычислять в SQL."
        
        return context
    
    def generate_sql(self, user_request: str, table_info: Dict[str, Any], 
                     temperature: float = 0.3, max_tokens: int = 500) -> str:
        """
        Generate SQL query based on user request
        
        Args:
            user_request: User's natural language request
            table_info: Information about the table structure
            temperature: Model temperature (0.0-1.0)
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated SQL query
            
        Raises:
            Exception: If API request fails
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self.api_key}"
        }
        
        system_context = self.build_context(table_info)
        
        payload = {
            "modelUri": f"gpt://{self.folder_id}/yandexgpt-lite",
            "completionOptions": {
                "temperature": temperature,
                "maxTokens": str(max_tokens)
            },
            "messages": [
                {
                    "role": "system",
                    "text": system_context
                },
                {
                    "role": "user",
                    "text": user_request
                }
            ]
        }
        
        response = requests.post(self.api_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            sql_text = result["result"]["alternatives"][0]["message"]["text"]
            return sql_text
        else:
            raise Exception(f"Ошибка API: {response.status_code}, {response.text}")


class ClickHouseHelper:
    """Helper class for working with ClickHouse"""
    
    def __init__(self, host: str = "localhost", port: int = 8123, 
                 user: str = "default", password: str = "", database: str = "default"):
        """
        Initialize ClickHouse helper
        
        Args:
            host: ClickHouse host
            port: ClickHouse HTTP port
            user: Database user
            password: Database password
            database: Database name
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.base_url = f"http://{host}:{port}"
    
    def execute_query(self, query: str) -> List[Dict]:
        """
        Execute SQL query and return results
        
        Args:
            query: SQL query to execute
            
        Returns:
            List of dictionaries with query results
            
        Raises:
            Exception: If query execution fails
        """
        params = {
            "user": self.user,
            "password": self.password,
            "database": self.database,
            "query": query
        }
        
        response = requests.get(self.base_url, params=params)
        
        if response.status_code == 200:
            # Parse response - assuming FORMAT JSON or JSONEachRow
            try:
                return response.json()
            except (json.JSONDecodeError, ValueError):
                # If not JSON, return raw text
                return [{"result": response.text}]
        else:
            raise Exception(f"Ошибка выполнения запроса: {response.status_code}, {response.text}")
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Get table structure information
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary with table information
        """
        # Basic validation to prevent SQL injection
        # Table names should only contain alphanumeric characters and underscores
        if not table_name.replace('_', '').isalnum():
            raise ValueError(f"Invalid table name: {table_name}. Only alphanumeric characters and underscores are allowed.")
        
        query = f"""
        SELECT 
            name,
            type,
            comment
        FROM system.columns
        WHERE database = '{self.database}' AND table = '{table_name}'
        FORMAT JSON
        """
        
        try:
            response = self.execute_query(query)
            columns = []
            
            if isinstance(response, dict) and 'data' in response:
                for row in response['data']:
                    columns.append({
                        'name': row.get('name', ''),
                        'type': row.get('type', ''),
                        'description': row.get('comment', '')
                    })
            
            return {
                'database': self.database,
                'table': table_name,
                'columns': columns,
                'description': f'Таблица {table_name} содержит данные из Яндекс Метрики'
            }
        except Exception as e:
            # Return minimal info if query fails
            return {
                'database': self.database,
                'table': table_name,
                'columns': [],
                'description': f'Таблица {table_name} содержит данные из Яндекс Метрики'
            }


def main():
    """Main function - example usage"""
    
    # Load configuration from environment variables
    API_KEY = os.getenv("YANDEX_API_KEY", "your_api_key_here")
    FOLDER_ID = os.getenv("YANDEX_FOLDER_ID", "your_folder_id_here")
    
    # ClickHouse configuration
    CH_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
    CH_PORT = int(os.getenv("CLICKHOUSE_PORT", "8123"))
    CH_USER = os.getenv("CLICKHOUSE_USER", "default")
    CH_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "")
    CH_DATABASE = os.getenv("CLICKHOUSE_DATABASE", "default")
    CH_TABLE = os.getenv("CLICKHOUSE_TABLE", "metrika_hits")
    
    # Initialize components
    sql_generator = YandexGPTSQLGenerator(API_KEY, FOLDER_ID)
    ch_helper = ClickHouseHelper(CH_HOST, CH_PORT, CH_USER, CH_PASSWORD, CH_DATABASE)
    
    print("=== yaGPT to SQL Generator ===")
    print(f"База данных: {CH_DATABASE}")
    print(f"Таблица: {CH_TABLE}")
    print()
    
    # Get table information
    print("Получение информации о таблице...")
    table_info = ch_helper.get_table_info(CH_TABLE)
    print(f"Найдено столбцов: {len(table_info['columns'])}")
    print()
    
    # Example user requests
    user_request = input("Введите ваш запрос (или нажмите Enter для примера): ").strip()
    
    if not user_request:
        user_request = "Напиши запрос, который найдёт топ-5 самых активных пользователей по количеству событий за последние 7 дней, с группировкой по стране."
        print(f"Используется пример: {user_request}")
    
    print()
    print("Генерация SQL запроса...")
    
    try:
        sql_query = sql_generator.generate_sql(user_request, table_info)
        print("\n" + "="*60)
        print("СГЕНЕРИРОВАННЫЙ SQL ЗАПРОС:")
        print("="*60)
        print(sql_query)
        print("="*60)
        
        # Ask if user wants to execute the query
        execute = input("\nВыполнить этот запрос? (y/n): ").strip().lower()
        
        if execute == 'y':
            print("\nВыполнение запроса...")
            try:
                results = ch_helper.execute_query(sql_query)
                print("\nРезультаты:")
                print(json.dumps(results, indent=2, ensure_ascii=False))
            except Exception as e:
                print(f"\nОшибка при выполнении запроса: {e}")
                print("Возможно, нужно добавить FORMAT JSON в конец запроса или проверить синтаксис.")
        
    except Exception as e:
        print(f"\nОшибка: {e}")
        print("\nПроверьте настройки API ключей и подключения к ClickHouse.")


if __name__ == "__main__":
    main()
