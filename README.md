# RAG-бот для QuantumForge Software

RAG-бот для работы с корпоративной базой знаний на основе технологий Retrieval-Augmented Generation.

## Быстрый старт

### Установка

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r config/requirements.txt
```

### Настройка

1. Настройте YandexGPT (см. `scripts/task4/ИНСТРУКЦИЯ.md`)
2. Создайте `.env` файл с API ключами

### Создание векторного индекса

```bash
python3 scripts/task3/step1_load_documents.py
python3 scripts/task3/step2_split_chunks.py
python3 scripts/task3/step3_create_embeddings.py
python3 scripts/task3/step4_create_index.py
```

### Запуск бота

Консольный режим:
```bash
python3 scripts/task4/run_rag_bot.py
```

Telegram-бот:
```bash
python3 scripts/task4/run_telegram_bot.py
```

## Технологии

- LLM: YandexGPT Pro
- Эмбеддинги: multilingual-e5-base (Sentence-Transformers)
- Векторная БД: ChromaDB
- Фреймворки: LangChain, python-telegram-bot

## Документация

- `Project_template.md` - описание всех решений проекта
- `scripts/task4/ИНСТРУКЦИЯ.md` - инструкция по настройке и запуску
- `TASK3_README.md` - описание векторного индекса
- `TASK4_README.md` - описание RAG-бота
- `TASK5_README.md` - описание защиты и тестирования
- `TASK5_RESULTS.md` - результаты тестирования безопасности

