"""
Скрипт для запуска Telegram-бота
"""
from rag_bot.telegram_bot import TelegramRAGBot


def main():
    """Запуск Telegram-бота"""
    bot = TelegramRAGBot()
    bot.run()


if __name__ == "__main__":
    main()

