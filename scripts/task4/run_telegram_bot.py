"""
Скрипт для запуска Telegram-бота
"""
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from rag_bot.telegram_bot import TelegramRAGBot


def main():
    """Запуск Telegram-бота"""
    bot = TelegramRAGBot()
    bot.run()


if __name__ == "__main__":
    main()

