#!/usr/bin/env python3
"""
Test script to verify .env file is being loaded correctly
"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Test reading environment variables
print("Проверка загрузки файла .env:")
print("=" * 60)

test_vars = [
    ("YANDEX_API_KEY", "your_api_key_here"),
    ("YANDEX_FOLDER_ID", "your_folder_id_here"),
    ("CLICKHOUSE_HOST", "localhost"),
    ("CLICKHOUSE_PORT", "8123"),
    ("CLICKHOUSE_USER", "default"),
    ("CLICKHOUSE_PASSWORD", ""),
    ("CLICKHOUSE_DATABASE", "default"),
    ("CLICKHOUSE_TABLE", "metrika_hits")
]

all_loaded = True
for var_name, default_value in test_vars:
    value = os.getenv(var_name, default_value)
    # Check if value is different from default (meaning it was loaded from .env)
    if value != default_value and value:
        print(f"✓ {var_name}: загружено из .env")
    else:
        print(f"✗ {var_name}: используется значение по умолчанию ({value})")
        all_loaded = False

print("=" * 60)
if all_loaded:
    print("✅ УСПЕХ: Все переменные окружения загружены из файла .env!")
else:
    print("⚠️  ВНИМАНИЕ: Некоторые переменные используют значения по умолчанию")
    print("Убедитесь, что:")
    print("  1. Файл .env существует в текущей директории")
    print("  2. Вы запускаете скрипт из директории, где находится .env")
    print("  3. В файле .env нет опечаток в именах переменных")
