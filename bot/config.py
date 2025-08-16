from decouple import config
import os

API_KEY_BYBIT = config("API_KEY_BYBIT", default=None)
API_SECRET_BYBIT = config("API_SECRET_BYBIT", default=None)

API_KEY_BINANCE = config("API_KEY_BINANCE", default=None)
API_SECRET_BINANCE = config("API_SECRET_BINANCE", default=None)

WEBHOOK_SECRET = config("WEBHOOK_SECRET")
DEFAULT_EXCHANGE = config("DEFAULT_EXCHANGE", default="bybit").lower()

TEST_MODE = config("TEST_MODE", default="True").lower() == "true"
TEST_BALANCE_USDT = float(config("TEST_BALANCE_USDT", default="100"))

# База данных - по умолчанию MySQL
USE_MYSQL = config("USE_MYSQL", default="True").lower() == "true"

# Путь к БД SQLite (только для локальной разработки)
DB_PATH = config("DB_PATH", default=os.path.join(os.path.dirname(__file__), "trades.db"))

# MySQL настройки (Railway переменные)
MYSQL_HOST = config("MYSQLHOST", default=config("MYSQL_HOST", default="localhost"))
MYSQL_PORT = int(config("MYSQLPORT", default=config("MYSQL_PORT", default="3306")))
MYSQL_USER = config("MYSQLUSER", default=config("MYSQL_USER", default="root"))
MYSQL_PASSWORD = config("MYSQLPASSWORD", default=config("MYSQL_ROOT_PASSWORD", default=""))
MYSQL_DATABASE = config("MYSQLDATABASE", default=config("MYSQL_DATABASE", default="railway"))

# Комиссии (в процентах) - теперь рассчитываются динамически
BYBIT_FEE = 0.1  # 0.1%
BINANCE_FEE = 0.1  # 0.1%

# Telegram настройки
TELEGRAM_BOT_TOKEN = config("TELEGRAM_BOT_TOKEN", default=None)
TELEGRAM_CHAT_ID = config("TELEGRAM_CHAT_ID", default=None)
TELEGRAM_ENABLED = config("TELEGRAM_ENABLED", default="False").lower() == "true"

# Telegram бот (для команд)
TELEGRAM_BOT_WEBHOOK_URL = config("TELEGRAM_BOT_WEBHOOK_URL", default=None)  # URL для webhook (опционально)
