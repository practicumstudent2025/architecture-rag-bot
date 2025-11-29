# Задание 3: Создание векторного индекса базы знаний

## Результаты выполнения

### 1. Модель эмбеддингов

- **Название**: `intfloat/multilingual-e5-base`
- **Репозиторий**: https://huggingface.co/intfloat/multilingual-e5-base
- **Размер эмбеддингов**: 768 измерений
- **Тип**: Локальная модель (Sentence-Transformers)
- **Обоснование выбора**: 
  - Поддержка мультиязычности (важно для международной компании)
  - Хорошее качество поиска
  - Работает на CPU, не требует GPU
  - Бесплатная (open-source)

### 2. База знаний

- **Источник**: `data/knowledge_base/`
- **Количество документов**: 31 файл
- **Формат**: `.txt` файлы с замененными терминами
- **Содержание**: Документы из вселенной Star Wars с замененными терминами

### 3. Разбиение на чанки

- **Метод**: `RecursiveCharacterTextSplitter` (LangChain)
- **Размер чанка**: 1000 символов (примерно 200-300 слов)
- **Перекрытие**: 100 символов
- **Разделители**: `\n\n`, `\n`, `. `, ` `, ``
- **Метаданные чанков**:
  - `source`: Имя исходного файла
  - `file_path`: Полный путь к файлу
  - `title`: Название документа
  - `chunk_id`: Уникальный идентификатор чанка
  - `chunk_size`: Размер чанка в символах

### 4. Векторная база данных

- **Название**: ChromaDB
- **Путь к индексу**: `data/vector_index/`
- **Тип**: Локальное хранилище с персистентностью
- **Особенности**: 
  - Встроенная поддержка метаданных
  - Автоматическое сохранение на диск
  - Быстрый поиск по векторным эмбеддингам

## Скрипты

### build_index.py
Скрипт для создания векторного индекса:
1. Загружает документы из `data/knowledge_base/`
2. Разбивает на чанки
3. Генерирует эмбеддинги с помощью `multilingual-e5-base`
4. Сохраняет индекс в ChromaDB
5. Тестирует поиск на примерах запросов
6. Сохраняет информацию об индексе в `index_info.json`

**Запуск:**
```bash
python3 scripts/build_index.py
```

### test_search.py
Скрипт для тестирования поиска по индексу:
- Демонстрирует примеры запросов
- Показывает найденные чанки с метаданными
- Позволяет проверить качество поиска

**Запуск:**
```bash
python3 scripts/test_search.py
```

## Пример запроса к индексу

```python
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Загрузка индекса
embeddings = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-base"
)
vectorstore = Chroma(
    persist_directory="data/vector_index",
    embedding_function=embeddings
)

# Поиск
query = "Кто такой Xarn Velgor?"
docs = vectorstore.similarity_search(query, k=3)

# Результаты
for doc in docs:
    print(f"Источник: {doc.metadata['source']}")
    print(f"Чанк ID: {doc.metadata['chunk_id']}")
    print(f"Текст: {doc.page_content[:200]}...")
```

## Статистика индекса

После выполнения `build_index.py` будет создан файл `data/vector_index/index_info.json` со следующей информацией:

- Количество чанков в индексе
- Время генерации индекса
- Параметры индексации
- Информация о модели и базе данных

## Файлы индекса

После создания индекса в `data/vector_index/` будут находиться:
- `chroma.sqlite3` - База данных ChromaDB
- `index_info.json` - Информация об индексе
- `test_results.json` - Результаты тестирования поиска
- `README.md` - Документация по использованию индекса

## Проверка качества

Скрипт автоматически тестирует поиск на следующих запросах:
1. "Кто такой Xarn Velgor?"
2. "Что такое Synth Flux?"
3. "Где находится Desertia?"

Результаты сохраняются в `test_results.json` и выводятся в консоль.

