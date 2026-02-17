"""
Example usage of yaGPT to SQL generator with mock data
This example demonstrates how to use the library without requiring actual API keys
"""

from yagpt_to_sql import YandexGPTSQLGenerator

# Example table information (similar to Yandex Metrica structure)
example_table_info = {
    'database': 'metrika',
    'table': 'hits',
    'description': 'Таблица содержит данные о просмотрах страниц из Яндекс Метрики',
    'columns': [
        {
            'name': 'EventDate',
            'type': 'Date',
            'description': 'Дата события'
        },
        {
            'name': 'EventTime',
            'type': 'DateTime',
            'description': 'Время события'
        },
        {
            'name': 'UserID',
            'type': 'UInt64',
            'description': 'Уникальный идентификатор пользователя'
        },
        {
            'name': 'SessionID',
            'type': 'UInt64',
            'description': 'Идентификатор сессии'
        },
        {
            'name': 'PageViews',
            'type': 'UInt32',
            'description': 'Количество просмотров страниц'
        },
        {
            'name': 'URL',
            'type': 'String',
            'description': 'URL страницы'
        },
        {
            'name': 'Referer',
            'type': 'String',
            'description': 'Источник перехода'
        },
        {
            'name': 'Country',
            'type': 'String',
            'description': 'Страна пользователя'
        },
        {
            'name': 'City',
            'type': 'String',
            'description': 'Город пользователя'
        },
        {
            'name': 'DeviceType',
            'type': 'String',
            'description': 'Тип устройства (desktop, mobile, tablet)'
        },
        {
            'name': 'Browser',
            'type': 'String',
            'description': 'Браузер пользователя'
        },
        {
            'name': 'OS',
            'type': 'String',
            'description': 'Операционная система'
        },
        {
            'name': 'Duration',
            'type': 'UInt32',
            'description': 'Длительность визита в секундах'
        }
    ]
}

def print_table_info(table_info):
    """Print table information in a nice format"""
    print("=" * 60)
    print(f"База данных: {table_info['database']}")
    print(f"Таблица: {table_info['table']}")
    print(f"Описание: {table_info['description']}")
    print("\nСтолбцы:")
    print("-" * 60)
    for col in table_info['columns']:
        print(f"  {col['name']:20} {col['type']:15} {col['description']}")
    print("=" * 60)

def demonstrate_context_building():
    """Demonstrate how context is built for the GPT model"""
    print("\n=== ДЕМОНСТРАЦИЯ: Построение контекста для модели ===\n")
    
    # Create a generator (with dummy credentials for demo)
    generator = YandexGPTSQLGenerator("demo_key", "demo_folder")
    
    # Build context
    context = generator.build_context(example_table_info)
    
    print("Контекст, который будет передан в Yandex GPT:")
    print("-" * 60)
    print(context)
    print("-" * 60)

def show_example_requests():
    """Show example user requests"""
    print("\n=== ПРИМЕРЫ ЗАПРОСОВ ПОЛЬЗОВАТЕЛЕЙ ===\n")
    
    examples = [
        "Найди топ-5 самых активных пользователей по количеству событий за последние 7 дней, с группировкой по стране",
        "Составь запрос для анализа сессий пользователей за вчера с фильтрацией по мобильным устройствам",
        "Выведи статистику по источникам трафика за последний месяц с группировкой по дням",
        "Найди самые популярные страницы по количеству просмотров за сегодня",
        "Покажи среднюю длительность сессии для пользователей из разных стран за последнюю неделю"
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example}")
    
    print()

def main():
    """Main demonstration function"""
    print("\n" + "=" * 60)
    print("  yaGPT to SQL - Демонстрация работы программы")
    print("=" * 60 + "\n")
    
    # Show table structure
    print("1. Структура таблицы с данными Яндекс Метрики:")
    print_table_info(example_table_info)
    
    # Show how context is built
    demonstrate_context_building()
    
    # Show example requests
    show_example_requests()
    
    print("\n" + "=" * 60)
    print("ПРИМЕЧАНИЕ:")
    print("=" * 60)
    print("""
Для запуска реальной генерации SQL запросов:

1. Настройте переменные окружения в файле .env:
   - YANDEX_API_KEY - ваш API ключ
   - YANDEX_FOLDER_ID - ваш folder ID
   - CLICKHOUSE_HOST, PORT, USER, PASSWORD, DATABASE, TABLE

2. Запустите основную программу:
   python yagpt_to_sql.py

3. Введите ваш запрос или используйте пример

Программа:
- Получит структуру таблицы из ClickHouse
- Отправит запрос в Yandex GPT с контекстом
- Получит сгенерированный SQL запрос
- Предложит выполнить запрос и покажет результаты
""")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
