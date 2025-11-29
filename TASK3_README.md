# Задание 3: Создание векторного индекса базы знаний

## Инструкция по выполнению (по шагам)

Выполняйте команды последовательно в терминале:

### ШАГ 1: Загрузка документов
```bash
python3 scripts/step1_load_documents.py
```
**Что делает:** Загружает все документы из `data/knowledge_base/`  
**Ожидаемое время:** 1-2 секунды  
**Результат:** Файл `data/processed/documents.pkl`

### ШАГ 2: Разбиение на чанки
```bash
python3 scripts/step2_split_chunks.py
```
**Что делает:** Разбивает документы на чанки по 1000 символов  
**Ожидаемое время:** 1-3 секунды  
**Результат:** Файл `data/processed/chunks.pkl`

### ШАГ 3: Инициализация модели эмбеддингов
```bash
python3 scripts/step3_create_embeddings.py
```
**Что делает:** Загружает модель `multilingual-e5-base` с Hugging Face  
**Ожидаемое время:** 1-2 минуты (при первом запуске, скачивание ~560 MB)  
**Результат:** Модель готова к использованию

### ШАГ 4: Создание векторного индекса
```bash
python3 scripts/step4_create_index.py
```
**Что делает:** Генерирует эмбеддинги для всех чанков и создает индекс в ChromaDB  
**Ожидаемое время:** 5-15 минут (зависит от количества чанков)  
**Результат:** Индекс в `data/vector_index/`

### ШАГ 5: Тестирование поиска
```bash
python3 scripts/test_search.py
```
**Что делает:** Тестирует поиск на примерах запросов  
**Ожидаемое время:** 10-30 секунд  
**Результат:** Результаты в `data/vector_index/test_results.json`

---

## Используемые технологии

### Модель эмбеддингов
- **Название**: `intfloat/multilingual-e5-base`
- **Репозиторий**: https://huggingface.co/intfloat/multilingual-e5-base
- **Размер эмбеддингов**: 768 измерений
- **Тип**: Локальная модель (Sentence-Transformers)

### Векторная база данных
- **Название**: ChromaDB
- **Путь**: `data/vector_index/`
- **Тип**: Локальное хранилище с персистентностью

### Параметры индексации
- **Размер чанка**: 1000 символов (~200-300 слов)
- **Перекрытие**: 100 символов
- **Метод разбиения**: RecursiveCharacterTextSplitter (LangChain)

---

## Результаты

После выполнения всех шагов будут созданы:

1. **Векторный индекс**: `data/vector_index/chroma.sqlite3`
2. **Информация об индексе**: `data/vector_index/index_info.json`
3. **Результаты тестирования**: `data/vector_index/test_results.json`
4. **Скрипты создания**: `scripts/step1_load_documents.py`, `step2_split_chunks.py`, `step3_create_embeddings.py`, `step4_create_index.py`

---

## Пример запроса к индексу

```python
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Загрузка индекса
embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-base")
vectorstore = Chroma(persist_directory="data/vector_index", embedding_function=embeddings)

# Поиск
query = "Кто такой Xarn Velgor?"
docs = vectorstore.similarity_search(query, k=3)

# Результаты
for doc in docs:
    print(f"Источник: {doc.metadata['source']}")
    print(f"Текст: {doc.page_content[:200]}...")
```

---

## Статистика

После выполнения шага 4 в `data/vector_index/index_info.json` будет информация:
- Количество чанков в индексе
- Время генерации индекса
- Параметры индексации

