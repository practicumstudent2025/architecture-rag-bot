"""
Конфигурация RAG-бота
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
BASE_DIR = Path(__file__).parent.parent
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Пути к данным
VECTOR_INDEX_DIR = BASE_DIR / "data" / "vector_index"
KNOWLEDGE_BASE_DIR = BASE_DIR / "data" / "knowledge_base"

# Модель эмбеддингов
EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-base"

# LLM настройки (можно переопределить через переменные окружения)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "yandex")  # openai, yandex, local
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY", "")
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID", "")

# Параметры поиска
SEARCH_K = 3  # Количество релевантных чанков для поиска
SIMILARITY_THRESHOLD = 0.7  # Порог релевантности (для "Я не знаю")

# Telegram настройки
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

