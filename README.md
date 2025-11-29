# RAG Bot для QuantumForge Software

Проект по созданию RAG-бота для работы с корпоративной базой знаний.

## Структура проекта

```
architecture-rag-bot/
├── config/                      # Конфигурационные файлы
│   └── terms_map.json           # Словарь замен терминов
├── data/                        # Данные проекта
│   ├── raw/                     # Исходные данные
│   │   └── pages/               # Скачанные HTML страницы
│   ├── processed/               # Обработанные данные
│   │   └── texts/               # Очищенные тексты
│   └── knowledge_base/          # Финальная база знаний
├── docs/                        # Документация
│   ├── research_task1.md       # Исследование моделей и инфраструктуры
│   └── Project_template.md      # Шаблон проекта
├── scripts/                     # Скрипты обработки
│   ├── download_pages.py        # Скачивание страниц
│   ├── clean_texts.py           # Очистка HTML
│   ├── replace_terms.py         # Замена терминов
│   └── rename_files.py          # Переименование файлов
├── requirements.txt             # Зависимости Python
└── README.md                    # Этот файл
```

## Установка

1. Создайте виртуальное окружение:
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate  # Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Использование

### Шаг 1: Скачивание страниц
```bash
python scripts/download_pages.py
```

### Шаг 2: Очистка текстов
```bash
python scripts/clean_texts.py
```

### Шаг 3: Замена терминов
```bash
python scripts/replace_terms.py
```

### Шаг 4: Переименование файлов (опционально)
```bash
python scripts/rename_files.py
```

## Описание папок

- **config/** - Конфигурационные файлы проекта
- **data/raw/** - Исходные данные (HTML страницы)
- **data/processed/** - Промежуточные обработанные данные
- **data/knowledge_base/** - Финальная база знаний для RAG
- **docs/** - Документация проекта
- **scripts/** - Скрипты для обработки данных

## Результаты

После выполнения всех скриптов в `data/knowledge_base/` будет создана база знаний из 31 документа с замененными терминами, готовая для использования в RAG-пайплайне.

