#!/usr/bin/env python3
"""
Тест добавления нового столбца через миграции
"""

import os
import sys

# Добавляем путь к модулям бота
sys.path.append(os.path.join(os.path.dirname(__file__)))

def test_new_migration():
    """Тест добавления нового столбца"""
    print("🧪 Тест добавления нового столбца")
    
    try:
        from bot.config import USE_MYSQL, DB_PATH
        
        if USE_MYSQL:
            print("   ❌ MySQL тест не поддерживается локально")
            return False
            
        # Подключаемся к SQLite
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Проверяем текущую структуру
        cur.execute("PRAGMA table_info(trades)")
        columns_before = [row[1] for row in cur.fetchall()]
        print(f"   Столбцы ДО: {columns_before}")
        
        # Добавляем тестовый столбец
        from bot.migrations import add_column_if_not_exists
        
        added = add_column_if_not_exists(cur, "trades", "test_column", "TEXT DEFAULT 'test'")
        
        if added:
            print("   ✅ Тестовый столбец добавлен")
            conn.commit()
            
            # Проверяем что столбец появился
            cur.execute("PRAGMA table_info(trades)")
            columns_after = [row[1] for row in cur.fetchall()]
            print(f"   Столбцы ПОСЛЕ: {columns_after}")
            
            if "test_column" in columns_after:
                print("   ✅ Столбец успешно создан")
                
                # Удаляем тестовый столбец (SQLite не поддерживает DROP COLUMN в старых версиях)
                print("   ⚠️ Тестовый столбец останется в БД (SQLite ограничение)")
            else:
                print("   ❌ Столбец не найден после создания")
                
        else:
            print("   ✅ Столбец уже существовал")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка теста: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_new_migration()
