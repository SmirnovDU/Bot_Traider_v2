#!/usr/bin/env python3
"""
Тест системы миграций
"""

import os
import sys

# Добавляем путь к модулям бота
sys.path.append(os.path.join(os.path.dirname(__file__)))

def test_migrations():
    """Тест системы миграций"""
    print("🧪 Тестирование системы миграций")
    
    try:
        from bot.migrations import apply_migrations
        from bot.config import USE_MYSQL
        
        print(f"   Режим БД: {'MySQL' if USE_MYSQL else 'SQLite'}")
        
        # Запускаем миграции
        apply_migrations()
        
        print("   ✅ Миграции применены успешно")
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка миграций: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_migrations()
