"""
Универсальный модуль для работы с базой данных.
Автоматически выбирает SQLite или MySQL в зависимости от конфигурации.
"""

from bot.config import USE_MYSQL

if USE_MYSQL:
    from bot.db_mysql import *
    print("🗄️ Используется MySQL база данных")
else:
    from bot.db import *
    print("🗄️ Используется SQLite база данных")
