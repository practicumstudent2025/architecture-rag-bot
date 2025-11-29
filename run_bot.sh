#!/bin/bash

# Переход в папку проекта
cd /Users/nataliashalaeva/YandexPractikum/architecture-rag-bot

# Активация виртуального окружения (если используется)
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Запуск RAG-бота
python scripts/task4/run_rag_bot.py

