"""
Telegram-бот для RAG-системы
"""
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from rag_bot.rag_pipeline import RAGBot
from rag_bot.config import TELEGRAM_BOT_TOKEN


class TelegramRAGBot:
    """Telegram-бот обертка для RAG-бота"""
    
    def __init__(self):
        self.rag_bot = RAGBot()
        self.app = None
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        await update.message.reply_text(
            "Привет! Я RAG-бот, который отвечает на вопросы на основе базы знаний.\n\n"
            "Задай мне любой вопрос, и я найду ответ в документах!"
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        query = update.message.text
        
        # Показываем, что бот думает
        await update.message.reply_text("Ищу информацию...")
        
        # Получаем ответ от RAG-бота
        result = self.rag_bot.answer_with_sources(query)
        answer = result["answer"]
        sources = result["sources"]
        
        # Формируем ответ с источниками
        response = answer
        if sources:
            response += "\n\n📚 Источники:\n" + "\n".join([f"• {s}" for s in sources])
        
        await update.message.reply_text(response)
    
    def run(self):
        """Запуск Telegram-бота"""
        if not TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN не установлен. Установите переменную окружения или в config.py")
        
        self.app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Регистрируем обработчики
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        print("Telegram-бот запущен!")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)

