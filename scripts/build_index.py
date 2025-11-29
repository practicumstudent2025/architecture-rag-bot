"""
Скрипт для создания векторного индекса базы знаний

Использует:
- Модель эмбеддингов: multilingual-e5-base (Sentence-Transformers)
- Векторная БД: ChromaDB
- Разбиение на чанки: LangChain RecursiveCharacterTextSplitter
"""
import os
import time
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
import json

# Конфигурация
KNOWLEDGE_BASE_DIR = os.path.join("data", "knowledge_base")
INDEX_DIR = os.path.join("data", "vector_index")
EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-base"
CHUNK_SIZE = 1000  # Размер чанка в символах (примерно 200-300 слов)
CHUNK_OVERLAP = 100  # Перекрытие между чанками


def load_documents():
    """
    Загружает все текстовые документы из базы знаний
    
    Returns:
        list: Список объектов Document с текстом и метаданными
    """
    print("\n" + "="*80)
    print("ШАГ 1: ЗАГРУЗКА ДОКУМЕНТОВ")
    print("="*80)
    
    documents = []
    txt_files = list(Path(KNOWLEDGE_BASE_DIR).glob("*.txt"))
    
    print(f"Найдено документов: {len(txt_files)}")
    print(f"Директория: {KNOWLEDGE_BASE_DIR}\n")
    
    for i, file_path in enumerate(txt_files, 1):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Создаем документ с метаданными
            doc = Document(
                page_content=content,
                metadata={
                    "source": str(file_path.name),
                    "file_path": str(file_path),
                    "title": file_path.stem
                }
            )
            documents.append(doc)
            print(f"[{i}/{len(txt_files)}] Загружен: {file_path.name} ({len(content):,} символов)")
        except Exception as e:
            print(f"❌ Ошибка при загрузке {file_path}: {e}")
    
    total_chars = sum(len(doc.page_content) for doc in documents)
    print(f"\n✅ Загружено документов: {len(documents)}")
    print(f"📊 Общий объем текста: {total_chars:,} символов")
    
    return documents


def split_documents(documents):
    """
    Разбивает документы на чанки
    
    Args:
        documents (list): Список документов
        
    Returns:
        list: Список чанков с метаданными
    """
    print("\n" + "="*80)
    print("ШАГ 2: РАЗБИЕНИЕ НА ЧАНКИ")
    print("="*80)
    
    # Создаем сплиттер с настройками
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    print(f"Параметры разбиения:")
    print(f"  - Размер чанка: {CHUNK_SIZE} символов (~200-300 слов)")
    print(f"  - Перекрытие: {CHUNK_OVERLAP} символов")
    print(f"  - Разделители: параграфы, строки, предложения, слова\n")
    print("Разбиение документов...")
    
    start_time = time.time()
    
    # Разбиваем все документы
    chunks = text_splitter.split_documents(documents)
    
    split_time = time.time() - start_time
    
    # Добавляем ID к каждому чанку
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i
        chunk.metadata["chunk_size"] = len(chunk.page_content)
    
    avg_chunk_size = sum(len(c.page_content) for c in chunks) / len(chunks) if chunks else 0
    
    print(f"\n✅ Создано чанков: {len(chunks):,}")
    print(f"⏱️  Время разбиения: {split_time:.2f} секунд")
    print(f"📊 Средний размер чанка: {avg_chunk_size:.0f} символов")
    
    return chunks


def create_embeddings():
    """
    Создает модель эмбеддингов
    
    Returns:
        HuggingFaceEmbeddings: Модель для генерации эмбеддингов
    """
    print("\n" + "="*80)
    print("ШАГ 3: ИНИЦИАЛИЗАЦИЯ МОДЕЛИ ЭМБЕДДИНГОВ")
    print("="*80)
    
    print(f"Модель: {EMBEDDING_MODEL_NAME}")
    print(f"Репозиторий: https://huggingface.co/{EMBEDDING_MODEL_NAME}")
    print(f"Размер эмбеддингов: 768 измерений")
    print(f"\n⚠️  ВНИМАНИЕ: Загрузка модели может занять 1-2 минуты при первом запуске")
    print(f"   Модель будет скачана с Hugging Face Hub (~560 MB)")
    print(f"   Пожалуйста, не прерывайте процесс!\n")
    
    start_time = time.time()
    
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={'device': 'cpu'}  # Используем CPU
    )
    
    load_time = time.time() - start_time
    
    print(f"✅ Модель загружена успешно")
    print(f"⏱️  Время загрузки: {load_time:.2f} секунд")
    
    return embeddings


def create_index(chunks, embeddings):
    """
    Создает векторный индекс в ChromaDB
    
    Args:
        chunks (list): Список чанков
        embeddings: Модель эмбеддингов
        
    Returns:
        Chroma: Векторное хранилище
    """
    print("\n" + "="*80)
    print("ШАГ 4: СОЗДАНИЕ ВЕКТОРНОГО ИНДЕКСА")
    print("="*80)
    
    print(f"Векторная БД: ChromaDB")
    print(f"Директория индекса: {INDEX_DIR}")
    print(f"Количество чанков для индексации: {len(chunks):,}")
    print(f"\n⚠️  ВНИМАНИЕ: Генерация эмбеддингов может занять значительное время")
    print(f"   Оценка времени: ~{len(chunks) * 0.05:.0f}-{len(chunks) * 0.1:.0f} секунд")
    print(f"   (~0.05-0.1 сек на чанк, зависит от размера)")
    print(f"   Пожалуйста, не прерывайте процесс!\n")
    
    start_time = time.time()
    
    print("Генерация эмбеддингов и создание индекса...")
    print("Это может занять несколько минут...\n")
    
    # Создаем векторное хранилище
    # ChromaDB автоматически генерирует эмбеддинги для всех чанков
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=INDEX_DIR
    )
    
    index_time = time.time() - start_time
    
    print(f"\n✅ Индекс создан и сохранен")
    print(f"⏱️  Время создания индекса: {index_time:.2f} секунд ({index_time/60:.2f} минут)")
    print(f"📁 Индекс сохранен в: {INDEX_DIR}")
    
    return vectorstore


def test_search(vectorstore, test_queries):
    """
    Тестирует поиск по индексу
    
    Args:
        vectorstore: Векторное хранилище
        test_queries (list): Список тестовых запросов
    """
    print("\n" + "="*80)
    print("ШАГ 5: ТЕСТИРОВАНИЕ ПОИСКА")
    print("="*80)
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Запрос: {query}")
        print("-" * 80)
        
        start_time = time.time()
        
        # Выполняем поиск
        docs = vectorstore.similarity_search(query, k=3)
        
        search_time = time.time() - start_time
        
        query_results = {
            "query": query,
            "found_chunks": len(docs),
            "search_time_seconds": round(search_time, 3),
            "results": []
        }
        
        for j, doc in enumerate(docs, 1):
            result = {
                "rank": j,
                "source": doc.metadata.get("source", "unknown"),
                "title": doc.metadata.get("title", "unknown"),
                "chunk_id": doc.metadata.get("chunk_id", "unknown"),
                "preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            }
            query_results["results"].append(result)
            
            print(f"\n  Результат {j}:")
            print(f"    📄 Источник: {result['source']}")
            print(f"    🆔 Чанк ID: {result['chunk_id']}")
            print(f"    📝 Превью: {result['preview']}")
        
        print(f"\n  ⏱️  Время поиска: {search_time:.3f} секунд")
        results.append(query_results)
    
    # Сохраняем результаты тестирования
    test_results_path = os.path.join(INDEX_DIR, "test_results.json")
    with open(test_results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Результаты тестирования сохранены в: {test_results_path}")
    
    return results


def save_index_info(chunks_count, processing_time, vectorstore):
    """
    Сохраняет информацию об индексе
    
    Args:
        chunks_count (int): Количество чанков
        processing_time (float): Время обработки
        vectorstore: Векторное хранилище
    """
    info = {
        "embedding_model": {
            "name": EMBEDDING_MODEL_NAME,
            "repository": f"https://huggingface.co/{EMBEDDING_MODEL_NAME}",
            "embedding_dimension": 768  # multilingual-e5-base имеет размерность 768
        },
        "vector_database": {
            "name": "ChromaDB",
            "index_path": INDEX_DIR
        },
        "knowledge_base": {
            "path": KNOWLEDGE_BASE_DIR,
            "documents_count": len(list(Path(KNOWLEDGE_BASE_DIR).glob("*.txt")))
        },
        "indexing": {
            "chunks_count": chunks_count,
            "chunk_size": CHUNK_SIZE,
            "chunk_overlap": CHUNK_OVERLAP,
            "processing_time_seconds": round(processing_time, 2),
            "processing_time_minutes": round(processing_time / 60, 2)
        }
    }
    
    info_path = os.path.join(INDEX_DIR, "index_info.json")
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Информация об индексе сохранена в: {info_path}")
    
    return info


def main():
    """Основная функция для создания векторного индекса"""
    total_start_time = time.time()
    
    print("="*80)
    print("СОЗДАНИЕ ВЕКТОРНОГО ИНДЕКСА БАЗЫ ЗНАНИЙ")
    print("="*80)
    print("\nЭтот процесс включает:")
    print("  1. Загрузку документов из базы знаний")
    print("  2. Разбиение на чанки")
    print("  3. Загрузку модели эмбеддингов")
    print("  4. Генерацию эмбеддингов и создание индекса")
    print("  5. Тестирование поиска")
    print("\n⚠️  ВАЖНО: Процесс может занять 5-15 минут в зависимости от:")
    print("  - Скорости интернета (при первой загрузке модели)")
    print("  - Производительности CPU")
    print("  - Количества документов и чанков")
    print("\n💡 Пожалуйста, не прерывайте процесс до завершения!")
    print("="*80)
    
    # Создаем директорию для индекса
    os.makedirs(INDEX_DIR, exist_ok=True)
    
    # 1. Загружаем документы
    documents = load_documents()
    
    if not documents:
        print("\n❌ ОШИБКА: Не найдено документов для индексации!")
        return
    
    # 2. Разбиваем на чанки
    chunks = split_documents(documents)
    
    # 3. Создаем модель эмбеддингов
    embeddings = create_embeddings()
    
    # 4. Создаем индекс
    vectorstore = create_index(chunks, embeddings)
    
    # Вычисляем общее время обработки
    total_processing_time = time.time() - total_start_time
    
    # Сохраняем информацию об индексе
    print("\n" + "="*80)
    print("СОХРАНЕНИЕ ИНФОРМАЦИИ ОБ ИНДЕКСЕ")
    print("="*80)
    index_info = save_index_info(len(chunks), total_processing_time, vectorstore)
    
    # Тестируем поиск
    test_queries = [
        "Кто такой Xarn Velgor?",
        "Что такое Synth Flux?",
        "Где находится Desertia?"
    ]
    test_results = test_search(vectorstore, test_queries)
    
    # Итоговая статистика
    print("\n" + "="*80)
    print("ИТОГОВАЯ СТАТИСТИКА")
    print("="*80)
    print(f"✅ Модель эмбеддингов: {EMBEDDING_MODEL_NAME}")
    print(f"✅ Векторная БД: ChromaDB")
    print(f"✅ Документов в базе: {index_info['knowledge_base']['documents_count']}")
    print(f"✅ Чанков в индексе: {index_info['indexing']['chunks_count']:,}")
    print(f"✅ Размер чанка: {CHUNK_SIZE} символов")
    print(f"✅ Общее время создания индекса: {index_info['indexing']['processing_time_seconds']:.2f} сек ({index_info['indexing']['processing_time_minutes']:.2f} мин)")
    print(f"✅ Индекс сохранен в: {INDEX_DIR}")
    print("="*80)
    print("\n🎉 Векторный индекс успешно создан!")


if __name__ == "__main__":
    main()
