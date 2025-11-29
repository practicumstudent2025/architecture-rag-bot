# Векторный индекс базы знаний

## Описание

Векторный индекс создан для быстрого семантического поиска по базе знаний RAG-бота.

## Использованные технологии

### Модель эмбеддингов
- **Название**: `intfloat/multilingual-e5-base`
- **Репозиторий**: https://huggingface.co/intfloat/multilingual-e5-base
- **Размер эмбеддингов**: 768 измерений
- **Тип**: Локальная модель (Sentence-Transformers)
- **Особенности**: Поддержка мультиязычности, оптимизирована для поиска

### Векторная база данных
- **Название**: ChromaDB
- **Тип**: Локальное хранилище
- **Путь**: `data/vector_index/`
- **Особенности**: Встроенная поддержка метаданных, персистентность

## Параметры индексации

- **Размер чанка**: 1000 символов (примерно 200-300 слов)
- **Перекрытие чанков**: 100 символов
- **Метод разбиения**: RecursiveCharacterTextSplitter (LangChain)
- **Разделители**: `\n\n`, `\n`, `. `, ` `, ``

## Метаданные чанков

Каждый чанк содержит следующие метаданные:
- `source`: Имя исходного файла
- `file_path`: Полный путь к файлу
- `title`: Название документа (без расширения)
- `chunk_id`: Уникальный идентификатор чанка
- `chunk_size`: Размер чанка в символах

## Использование

### Загрузка индекса

```python
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-base"
)

vectorstore = Chroma(
    persist_directory="data/vector_index",
    embedding_function=embeddings
)
```

### Поиск по индексу

```python
# Поиск похожих документов
docs = vectorstore.similarity_search("ваш запрос", k=5)

# Поиск с метаданными
docs = vectorstore.similarity_search_with_score("ваш запрос", k=5)
```

## Файлы индекса

- `chroma.sqlite3` - База данных ChromaDB
- `index_info.json` - Информация об индексе
- `test_results.json` - Результаты тестирования поиска

