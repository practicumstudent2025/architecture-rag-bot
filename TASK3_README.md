# Задание 3: Создание векторного индекса базы знаний

## Итоговые результаты

**Модель эмбеддингов:**
- `intfloat/multilingual-e5-base` (768 измерений)

**База знаний:**
- 31 документ из `data/knowledge_base/`

**Векторный индекс:**
- **Количество чанков**: 9,119
- **Время генерации**: 10.67 минут (640.27 секунд)
- **Векторная БД**: ChromaDB
- **Путь**: `data/vector_index/`

**Тестирование поиска:**
- Все 3 тестовых запроса выполнены успешно
- Время поиска: 0.034–0.096 секунд
- Найдены релевантные чанки для каждого запроса

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

## Скрипты создания индекса

Процесс разбит на 5 шагов:

1. **step1_load_documents.py** - Загрузка документов
2. **step2_split_chunks.py** - Разбиение на чанки
3. **step3_create_embeddings.py** - Инициализация модели эмбеддингов
4. **step4_create_index.py** - Создание векторного индекса
5. **step5_test_search.py** - Тестирование поиска

## Пример запроса к индексу

### Запрос: "Кто такой Xarn Velgor?"

**Найденные чанки:**

1. **Источник**: `Xarn_Velgor.txt`
   - **Чанк ID**: 3156
   - **Превью**: "Xarn Velgor (2017) 21..."

2. **Источник**: `Anakin_Thorne.txt`
   - **Чанк ID**: 6643
   - **Превью**: "Xarn Velgor (2017) 21..."

3. **Источник**: `Xarn_Velgor.txt`
   - **Чанк ID**: 2576
   - **Превью**: "Xarn Velgor is attacked by memories of his past"

**Время поиска**: 0.096 секунд

### Запрос: "Что такое Synth Flux?"

**Найденные чанки:**

1. **Источник**: `Synth_Flux.txt`
   - **Чанк ID**: 1214
   - **Превью**: "Synth Flux was an energy field created by all life that bound everything in the universe together..."

2. **Источник**: `Emperor_Malachar.txt`
   - **Чанк ID**: 6741
   - **Превью**: "Synth Flux Shadow Realm of Synth Flux..."

3. **Источник**: `Synth_Flux.txt`
   - **Чанк ID**: 1285
   - **Превью**: "A leitmotif of Synth Flux exists..."

**Время поиска**: 0.034 секунд

### Запрос: "Где находится Desertia?"

**Найденные чанки:**

1. **Источник**: `Desertia.txt`
   - **Чанк ID**: 6747
   - **Превью**: "Desertia was a sparsely i..."

2. **Источник**: `Desertia.txt`
   - **Чанк ID**: 6885
   - **Превью**: "Star Wars: The Book of Boba Fett..."

3. **Источник**: `Desertia.txt`
   - **Чанк ID**: 6742
   - **Превью**: "Desertia I have a bad feeling about this…"

**Время поиска**: 0.034 секунд

## Статистика индекса

- **Количество чанков**: 9,119
- **Время генерации индекса**: 640.27 секунд (10.67 минут)
- **Путь к индексу**: `data/vector_index/`

Детальная информация сохранена в `data/vector_index/index_info.json`

## Файлы результата

- **Векторный индекс**: `data/vector_index/chroma.sqlite3`
- **Информация об индексе**: `data/vector_index/index_info.json`
- **Результаты тестирования**: `data/vector_index/test_results.json`
- **Скрипты создания**: `scripts/step1_load_documents.py`, `step2_split_chunks.py`, `step3_create_embeddings.py`, `step4_create_index.py`
- **Скрипт тестирования**: `scripts/step5_test_search.py`

## Использование индекса

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
    print(f"Чанк ID: {doc.metadata['chunk_id']}")
    print(f"Текст: {doc.page_content[:200]}...")
```
