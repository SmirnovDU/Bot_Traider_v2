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

# Путь к БД относительно папки bot
DB_PATH = os.path.join(os.path.dirname(__file__), "trades.db")

# Комиссии (в процентах) - теперь рассчитываются динамически
BYBIT_FEE = 0.1  # 0.1%
BINANCE_FEE = 0.1  # 0.1%

# Telegram настройки
TELEGRAM_BOT_TOKEN = config("TELEGRAM_BOT_TOKEN", default=None)
TELEGRAM_CHAT_ID = config("TELEGRAM_CHAT_ID", default=None)
TELEGRAM_ENABLED = config("TELEGRAM_ENABLED", default="False").lower() == "true"
