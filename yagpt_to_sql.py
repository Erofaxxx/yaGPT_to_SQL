"""
yaGPT to SQL - Program for generating ClickHouse SQL queries using Yandex GPT
"""

import os
import requests
from typing import Dict, List, Optional, Any
import json
from dotenv import load_dotenv
import logging
import re


def clean_sql_query(sql_text: str) -> str:
    """
    Clean SQL query by removing markdown code blocks and extra whitespace
    
    Args:
        sql_text: SQL query text that may contain markdown formatting
        
    Returns:
        Cleaned SQL query without markdown formatting
    """
    # Remove markdown code blocks (```sql ... ``` or ``` ... ```)
    # This handles the common case where Yandex GPT wraps SQL in code blocks
    
    cleaned = sql_text.strip()
    
    # Check if starts with ``` and ends with ```
    if cleaned.startswith('```') and cleaned.endswith('```'):
        # Remove opening marker: ``` or ```sql or ```python etc.
        lines = cleaned.split('\n', 1)
        if len(lines) > 1 and lines[0].startswith('```'):
            # Remove first line (opening marker)
            cleaned = lines[1]
        else:
            # Single line or no newline after opening marker
            cleaned = cleaned[3:]  # Remove opening ```
        
        # Remove closing marker: ```
        if cleaned.endswith('```'):
            lines = cleaned.rsplit('\n', 1)
            if len(lines) > 1 and lines[-1] == '```':
                # Remove last line (closing marker)
                cleaned = lines[0]
            else:
                # No newline before closing marker
                cleaned = cleaned[:-3]
    
    # Strip any remaining whitespace
    cleaned = cleaned.strip()
    
    return cleaned


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
                 user: str = "default", password: str = "", database: str = "default",
                 ssl_cert_path: str = None):
        """
        Initialize ClickHouse helper
        
        Args:
            host: ClickHouse host (can include protocol like https://...)
            port: ClickHouse HTTP port
            user: Database user
            password: Database password
            database: Database name
            ssl_cert_path: SSL certificate configuration:
                          - String path (e.g., 'YandexInternalRootCA.crt') - uses custom certificate file
                          - None or empty string - uses system certificates (default)
                          - Boolean False - disables SSL verification (not recommended for production)
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        
        # Handle SSL certificate configuration
        # ssl_cert_path can be: string (cert path), None/empty (system certs), or False (disabled)
        if ssl_cert_path is False:
            # Explicitly disabled with boolean False
            self.verify_ssl = False
        elif ssl_cert_path:
            # Use provided certificate file (string path)
            self.verify_ssl = ssl_cert_path
        else:
            # Default: use system certificates (None or empty string)
            self.verify_ssl = True
        
        # Construct base URL - handle if host already includes protocol
        if host.startswith('http://') or host.startswith('https://'):
            # Host already includes protocol
            self.base_url = f"{host}:{port}"
        else:
            # Default to http if no protocol specified
            self.base_url = f"http://{host}:{port}"
        
        logging.info(f"ClickHouse connection: {self.base_url}, database: {database}")
        
        # Log SSL configuration
        if self.base_url.startswith('https://'):
            if self.verify_ssl is False:
                logging.warning("⚠️  SSL certificate verification ОТКЛЮЧЕНА! Это небезопасно для продакшена.")
                logging.warning("⚠️  SSL certificate verification DISABLED! This is insecure for production.")
            elif isinstance(self.verify_ssl, str):
                logging.info(f"✓ SSL verification enabled with certificate: {self.verify_ssl}")
            else:
                logging.info("✓ SSL verification enabled with system certificates")
    
    def execute_query(self, query: str, timeout: int = None) -> List[Dict]:
        """
        Execute SQL query and return results
        
        Args:
            query: SQL query to execute
            timeout: Request timeout in seconds (default from env or 30)
            
        Returns:
            List of dictionaries with query results
            
        Raises:
            Exception: If query execution fails
        """
        if timeout is None:
            timeout = int(os.getenv("CLICKHOUSE_TIMEOUT", "30"))
        
        params = {
            "user": self.user,
            "password": self.password,
            "database": self.database,
            "query": query
        }
        
        logging.debug(f"Executing query to {self.base_url}")
        logging.debug(f"Query: {query[:200]}...")  # Log first 200 chars
        
        try:
            response = requests.get(self.base_url, params=params, timeout=timeout, verify=self.verify_ssl)
            
            if response.status_code == 200:
                # Parse response - assuming FORMAT JSON or JSONEachRow
                try:
                    result = response.json()
                    logging.debug(f"Query successful, response type: {type(result)}")
                    return result
                except (json.JSONDecodeError, ValueError) as e:
                    # If not JSON, return raw text
                    logging.warning(f"Response is not JSON: {e}")
                    return [{"result": response.text}]
            else:
                error_msg = f"Ошибка выполнения запроса: {response.status_code}, {response.text}"
                logging.error(error_msg)
                raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"Ошибка соединения с ClickHouse: {e}"
            logging.error(error_msg)
            raise Exception(error_msg)
    
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
            logging.info(f"Запрос структуры таблицы: {self.database}.{table_name}")
            response = self.execute_query(query)
            columns = []
            
            if isinstance(response, dict) and 'data' in response:
                for row in response['data']:
                    columns.append({
                        'name': row.get('name', ''),
                        'type': row.get('type', ''),
                        'description': row.get('comment', '')
                    })
                logging.info(f"Найдено столбцов: {len(columns)}")
            else:
                logging.warning(f"Неожиданный формат ответа: {type(response)}")
                logging.debug(f"Response content: {response}")
            
            return {
                'database': self.database,
                'table': table_name,
                'columns': columns,
                'description': f'Таблица {table_name} содержит данные из Яндекс Метрики'
            }
        except Exception as e:
            # Log the error but return minimal info
            logging.error(f"Ошибка при получении информации о таблице: {e}")
            logging.error(f"Убедитесь, что:")
            logging.error(f"  1. Таблица '{table_name}' существует в базе данных '{self.database}'")
            logging.error(f"  2. У пользователя '{self.user}' есть права на чтение структуры таблицы")
            logging.error(f"  3. Параметры подключения к ClickHouse верны")
            return {
                'database': self.database,
                'table': table_name,
                'columns': [],
                'description': f'Таблица {table_name} содержит данные из Яндекс Метрики'
            }


def main():
    """Main function - example usage"""
    
    # Configure logging
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    # Validate log level
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if log_level not in valid_levels:
        print(f"⚠ Неверный уровень логирования '{log_level}', используется INFO")
        log_level = "INFO"
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Load environment variables from .env file
    load_dotenv()
    
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
    
    # SSL certificate configuration
    # Priority: CLICKHOUSE_SSL_CERT_PATH > CLICKHOUSE_SSL_VERIFY
    # Result can be: string (cert path), None (system certs), or False (disabled)
    ssl_cert_config = os.getenv("CLICKHOUSE_SSL_CERT_PATH", "")
    
    if ssl_cert_config:
        # Use specified certificate file
        CH_SSL_CERT = ssl_cert_config
    else:
        # Check old CLICKHOUSE_SSL_VERIFY for backwards compatibility
        ssl_verify_str = os.getenv("CLICKHOUSE_SSL_VERIFY", "true").lower()
        if ssl_verify_str in ["false", "0", "no", "off"]:
            CH_SSL_CERT = False  # Boolean False to disable
        else:
            CH_SSL_CERT = None  # None to use system certificates
    
    print("=== yaGPT to SQL Generator ===")
    print(f"База данных: {CH_DATABASE}")
    print(f"Таблица: {CH_TABLE}")
    print()
    
    # Initialize components
    logging.info("Инициализация компонентов...")
    sql_generator = YandexGPTSQLGenerator(API_KEY, FOLDER_ID)
    ch_helper = ClickHouseHelper(CH_HOST, CH_PORT, CH_USER, CH_PASSWORD, CH_DATABASE, CH_SSL_CERT)
    
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
                # Clean the SQL query to remove markdown formatting
                cleaned_sql = clean_sql_query(sql_query)
                logging.debug(f"Cleaned SQL: {cleaned_sql}")
                
                results = ch_helper.execute_query(cleaned_sql)
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
