#!/usr/bin/env python3
"""
Test script to verify error logging and connection handling
"""

import os
import logging
from dotenv import load_dotenv

# Import from current directory
try:
    from yagpt_to_sql import ClickHouseHelper
except ImportError:
    import sys
    # Add current directory to path only if import fails
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from yagpt_to_sql import ClickHouseHelper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

# Load environment
load_dotenv()

print("=" * 70)
print("TEST: ClickHouse Connection and Error Logging")
print("=" * 70)
print()

# Get configuration
CH_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CH_PORT = int(os.getenv("CLICKHOUSE_PORT", "8123"))
CH_USER = os.getenv("CLICKHOUSE_USER", "default")
CH_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "")
CH_DATABASE = os.getenv("CLICKHOUSE_DATABASE", "default")
CH_TABLE = os.getenv("CLICKHOUSE_TABLE", "metrika_hits")

# SSL verification (default: True for security)
ssl_verify_str = os.getenv("CLICKHOUSE_SSL_VERIFY", "true").lower()
CH_SSL_VERIFY = ssl_verify_str not in ["false", "0", "no", "off"]

print(f"Configuration:")
print(f"  Host: {CH_HOST}")
print(f"  Port: {CH_PORT}")
print(f"  User: {CH_USER}")
print(f"  Database: {CH_DATABASE}")
print(f"  Table: {CH_TABLE}")
print(f"  SSL Verify: {CH_SSL_VERIFY}")
print()

# Test 1: Initialize ClickHouse helper
print("Test 1: Initialize ClickHouse helper")
print("-" * 70)
try:
    ch_helper = ClickHouseHelper(CH_HOST, CH_PORT, CH_USER, CH_PASSWORD, CH_DATABASE, CH_SSL_VERIFY)
    print(f"✓ Base URL: {ch_helper.base_url}")
    print(f"✓ SSL Verify: {ch_helper.verify_ssl}")
    print()
except Exception as e:
    print(f"✗ Failed to initialize: {e}")
    print()
    sys.exit(1)

# Test 2: Get table info
print("Test 2: Get table information")
print("-" * 70)
try:
    table_info = ch_helper.get_table_info(CH_TABLE)
    print(f"Результат:")
    print(f"  Database: {table_info['database']}")
    print(f"  Table: {table_info['table']}")
    print(f"  Columns found: {len(table_info['columns'])}")
    
    if table_info['columns']:
        print(f"\nПервые 5 столбцов:")
        for i, col in enumerate(table_info['columns'][:5], 1):
            print(f"    {i}. {col['name']} ({col['type']})")
    else:
        print("\n⚠ Столбцы не найдены - проверьте логи ошибок выше")
    print()
except Exception as e:
    print(f"✗ Failed: {e}")
    print()

print("=" * 70)
print("Test complete. Check the logs above for any errors.")
print("=" * 70)
