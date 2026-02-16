#!/usr/bin/env python3
"""
Example usage of the Yandex GPT to ClickHouse SQL Generator.
"""

from yagpt_to_sql import YandexGPTSQLGenerator, ClickHouseTableSchema, create_default_metrika_schema
import os


def example_basic_usage():
    """Basic usage example."""
    print("=== Example 1: Basic Usage ===\n")

    # Get credentials from environment
    api_key = os.getenv("YANDEX_API_KEY", "your_api_key_here")
    folder_id = os.getenv("YANDEX_FOLDER_ID", "your_folder_id_here")

    # Use default Metrika schema
    schema = create_default_metrika_schema()
    generator = YandexGPTSQLGenerator(api_key, folder_id)

    # Example request
    user_request = "Найди топ-5 самых популярных страниц за последние 7 дней"

    try:
        sql_query = generator.generate_sql(user_request, schema)
        print(f"Запрос: {user_request}")
        print(f"\nСгенерированный SQL:\n{sql_query}\n")
    except Exception as e:
        print(f"Ошибка: {e}\n")


def example_custom_schema():
    """Example with custom table schema."""
    print("=== Example 2: Custom Schema ===\n")

    api_key = os.getenv("YANDEX_API_KEY", "your_api_key_here")
    folder_id = os.getenv("YANDEX_FOLDER_ID", "your_folder_id_here")

    # Define custom schema
    columns = {
        "date": "Дата транзакции (Date)",
        "user_id": "ID пользователя (UInt64)",
        "product_id": "ID товара (UInt32)",
        "category": "Категория товара (String)",
        "amount": "Сумма покупки (Decimal(10,2))",
        "quantity": "Количество (UInt16)",
        "payment_method": "Способ оплаты (String)",
        "status": "Статус заказа (String)"
    }

    schema = ClickHouseTableSchema(
        database="ecommerce",
        table="orders",
        columns=columns,
        description="Таблица с данными о заказах в интернет-магазине"
    )

    generator = YandexGPTSQLGenerator(api_key, folder_id)

    user_request = "Покажи топ-10 самых продаваемых товаров за последний месяц с общей суммой продаж"

    try:
        sql_query = generator.generate_sql(user_request, schema)
        print(f"Запрос: {user_request}")
        print(f"\nСгенерированный SQL:\n{sql_query}\n")
    except Exception as e:
        print(f"Ошибка: {e}\n")


def example_multiple_requests():
    """Example with multiple requests."""
    print("=== Example 3: Multiple Requests ===\n")

    api_key = os.getenv("YANDEX_API_KEY", "your_api_key_here")
    folder_id = os.getenv("YANDEX_FOLDER_ID", "your_folder_id_here")

    schema = create_default_metrika_schema()
    generator = YandexGPTSQLGenerator(api_key, folder_id)

    requests = [
        "Посчитай количество уникальных пользователей за сегодня",
        "Найди среднюю длительность сессии по устройствам",
        "Покажи распределение трафика по источникам за последнюю неделю",
        "Выведи процент отказов по каждому часу дня"
    ]

    for i, request in enumerate(requests, 1):
        print(f"Запрос {i}: {request}")
        try:
            sql_query = generator.generate_sql(request, schema, temperature=0.2)
            print(f"SQL:\n{sql_query}\n")
        except Exception as e:
            print(f"Ошибка: {e}\n")
        print("-" * 80)


def example_with_different_temperatures():
    """Example showing effect of temperature parameter."""
    print("=== Example 4: Different Temperatures ===\n")

    api_key = os.getenv("YANDEX_API_KEY", "your_api_key_here")
    folder_id = os.getenv("YANDEX_FOLDER_ID", "your_folder_id_here")

    schema = create_default_metrika_schema()
    generator = YandexGPTSQLGenerator(api_key, folder_id)

    user_request = "Найди пользователей с самыми длинными сессиями"

    for temp in [0.1, 0.5, 0.9]:
        print(f"Temperature = {temp}")
        try:
            sql_query = generator.generate_sql(user_request, schema, temperature=temp)
            print(f"SQL:\n{sql_query}\n")
        except Exception as e:
            print(f"Ошибка: {e}\n")
        print("-" * 80)


if __name__ == "__main__":
    # Check if credentials are set
    if not os.getenv("YANDEX_API_KEY") or not os.getenv("YANDEX_FOLDER_ID"):
        print("⚠️  Внимание: Не установлены переменные окружения YANDEX_API_KEY и YANDEX_FOLDER_ID")
        print("Примеры будут запущены с placeholder значениями и завершатся с ошибкой.")
        print("\nДля реального использования установите:")
        print("  export YANDEX_API_KEY='your_api_key'")
        print("  export YANDEX_FOLDER_ID='your_folder_id'")
        print("\n" + "=" * 80 + "\n")

    # Run examples
    example_basic_usage()
    example_custom_schema()

    # Uncomment to run more examples:
    # example_multiple_requests()
    # example_with_different_temperatures()
