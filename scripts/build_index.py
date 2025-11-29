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
    documents = []
    txt_files = list(Path(KNOWLEDGE_BASE_DIR).glob("*.txt"))
    
    print(f"Найдено документов: {len(txt_files)}")
    
    for file_path in txt_files:
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
            print(f"Загружен: {file_path.name}")
        except Exception as e:
            print(f"Ошибка при загрузке {file_path}: {e}")
    
    return documents


def split_documents(documents):
    """
    Разбивает документы на чанки
    
    Args:
        documents (list): Список документов
        
    Returns:
        list: Список чанков с метаданными
    """
    # Создаем сплиттер с настройками
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    print(f"\nРазбиение документов на чанки...")
    print(f"Размер чанка: {CHUNK_SIZE} символов")
    print(f"Перекрытие: {CHUNK_OVERLAP} символов")
    
    # Разбиваем все документы
    chunks = text_splitter.split_documents(documents)
    
    # Добавляем ID к каждому чанку
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i
        chunk.metadata["chunk_size"] = len(chunk.page_content)
    
    print(f"Создано чанков: {len(chunks)}")
    
    return chunks


def create_embeddings():
    """
    Создает модель эмбеддингов
    
    Returns:
        HuggingFaceEmbeddings: Модель для генерации эмбеддингов
    """
    print(f"\nЗагрузка модели эмбеддингов: {EMBEDDING_MODEL_NAME}")
    print("Это может занять некоторое время при первом запуске...")
    
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={'device': 'cpu'}  # Используем CPU
    )
    
    print("Модель загружена успешно")
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
    print(f"\nСоздание векторного индекса в ChromaDB...")
    print(f"Директория индекса: {INDEX_DIR}")
    
    # Создаем векторное хранилище
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=INDEX_DIR
    )
    
    print("Индекс создан и сохранен")
    return vectorstore


def test_search(vectorstore, test_queries):
    """
    Тестирует поиск по индексу
    
    Args:
        vectorstore: Векторное хранилище
        test_queries (list): Список тестовых запросов
    """
    print("\n" + "="*80)
    print("ТЕСТИРОВАНИЕ ПОИСКА")
    print("="*80)
    
    results = []
    
    for query in test_queries:
        print(f"\nЗапрос: {query}")
        print("-" * 80)
        
        # Выполняем поиск
        docs = vectorstore.similarity_search(query, k=3)
        
        query_results = {
            "query": query,
            "found_chunks": len(docs),
            "results": []
        }
        
        for i, doc in enumerate(docs, 1):
            result = {
                "rank": i,
                "source": doc.metadata.get("source", "unknown"),
                "title": doc.metadata.get("title", "unknown"),
                "chunk_id": doc.metadata.get("chunk_id", "unknown"),
                "preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            }
            query_results["results"].append(result)
            
            print(f"\n{i}. Источник: {result['source']}")
            print(f"   Чанк ID: {result['chunk_id']}")
            print(f"   Превью: {result['preview']}")
        
        results.append(query_results)
    
    # Сохраняем результаты тестирования
    test_results_path = os.path.join(INDEX_DIR, "test_results.json")
    with open(test_results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nРезультаты тестирования сохранены в: {test_results_path}")
    
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
    
    print(f"\nИнформация об индексе сохранена в: {info_path}")
    
    return info


def main():
    """Основная функция для создания векторного индекса"""
    start_time = time.time()
    
    print("="*80)
    print("СОЗДАНИЕ ВЕКТОРНОГО ИНДЕКСА БАЗЫ ЗНАНИЙ")
    print("="*80)
    
    # Создаем директорию для индекса
    os.makedirs(INDEX_DIR, exist_ok=True)
    
    # 1. Загружаем документы
    print("\n[1/4] Загрузка документов...")
    documents = load_documents()
    
    # 2. Разбиваем на чанки
    print("\n[2/4] Разбиение на чанки...")
    chunks = split_documents(documents)
    
    # 3. Создаем модель эмбеддингов
    print("\n[3/4] Инициализация модели эмбеддингов...")
    embeddings = create_embeddings()
    
    # 4. Создаем индекс
    print("\n[4/4] Создание векторного индекса...")
    vectorstore = create_index(chunks, embeddings)
    
    # Вычисляем время обработки
    processing_time = time.time() - start_time
    
    # Сохраняем информацию об индексе
    print("\n[Дополнительно] Сохранение информации об индексе...")
    index_info = save_index_info(len(chunks), processing_time, vectorstore)
    
    # Тестируем поиск
    print("\n[Дополнительно] Тестирование поиска...")
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
    print(f"Модель эмбеддингов: {EMBEDDING_MODEL_NAME}")
    print(f"Векторная БД: ChromaDB")
    print(f"Документов в базе: {index_info['knowledge_base']['documents_count']}")
    print(f"Чанков в индексе: {index_info['indexing']['chunks_count']}")
    print(f"Размер чанка: {CHUNK_SIZE} символов")
    print(f"Время создания индекса: {index_info['indexing']['processing_time_seconds']} сек ({index_info['indexing']['processing_time_minutes']} мин)")
    print(f"Индекс сохранен в: {INDEX_DIR}")
    print("="*80)


if __name__ == "__main__":
    main()

