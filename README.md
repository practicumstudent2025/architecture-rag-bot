# RAG-бот для QuantumForge Software

RAG-бот для работы с корпоративной базой знаний на основе технологий Retrieval-Augmented Generation.

## Структура проекта

```
architecture-rag-bot/
├── rag_bot/              # Основной модуль RAG-бота
│   ├── config.py         # Конфигурация
│   ├── vector_store.py   # Работа с векторным хранилищем
│   ├── llm_providers.py  # Провайдеры LLM
│   ├── prompts.py        # Создание промптов
│   ├── rag_pipeline.py  # RAG-пайплайн
│   ├── security.py       # Защита от промпт-инъекций
│   └── telegram_bot.py   # Telegram-бот
├── scripts/              # Скрипты по заданиям
│   ├── task2/           # Подготовка базы знаний
│   ├── task3/           # Создание векторного индекса
│   ├── task4/           # Запуск RAG-бота
│   └── task5/            # Тестирование безопасности
├── data/                 # Данные
│   ├── knowledge_base/   # База знаний (31 документ)
│   ├── vector_index/     # Векторный индекс
│   └── logs/            # Логи
└── config/              # Конфигурация
    └── requirements.txt  # Зависимости
```

## Установка

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r config/requirements.txt
```

## Настройка YandexGPT

1. Создайте каталог в Yandex Cloud
2. Создайте сервисный аккаунт
3. Назначьте роль `ai.languageModels.user` через Access bindings каталога
4. Создайте API ключ со scope `yc.ai.languageModels.execute`
5. Создайте `.env` файл (см. `.env.example`)

Подробная инструкция в `ИНСТРУКЦИЯ.md`

## Создание векторного индекса

```bash
python3 scripts/task3/step1_load_documents.py
python3 scripts/task3/step2_split_chunks.py
python3 scripts/task3/step3_create_embeddings.py
python3 scripts/task3/step4_create_index.py
```

## Запуск бота

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

- `ИНСТРУКЦИЯ.md` - инструкция по настройке и запуску
- `Project_template.md` - описание всех решений проекта
- `research_task1.md` - исследование моделей и инфраструктуры
- `TASK3_README.md` - описание векторного индекса
- `TASK4_README.md` - описание RAG-бота
- `TASK5_README.md` - описание защиты и тестирования
- `TASK5_RESULTS.md` - результаты тестирования безопасности

