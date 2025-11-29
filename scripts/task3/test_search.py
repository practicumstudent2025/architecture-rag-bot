"""
Скрипт для тестирования поиска по векторному индексу

Демонстрирует примеры запросов и найденные чанки
"""
import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

INDEX_DIR = os.path.join("data", "vector_index")
EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-base"


def load_index():
    """Загружает векторный индекс"""
    print("Загрузка модели эмбеддингов...")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={'device': 'cpu'}
    )
    
    print("Загрузка векторного индекса...")
    vectorstore = Chroma(
        persist_directory=INDEX_DIR,
        embedding_function=embeddings
    )
    
    print("Индекс загружен успешно\n")
    return vectorstore


def test_query(vectorstore, query, k=3):
    """
    Тестирует поиск по запросу
    
    Args:
        vectorstore: Векторное хранилище
        query (str): Поисковый запрос
        k (int): Количество результатов
    """
    print("="*80)
    print(f"ЗАПРОС: {query}")
    print("="*80)
    
    # Выполняем поиск
    docs = vectorstore.similarity_search(query, k=k)
    
    print(f"\nНайдено результатов: {len(docs)}\n")
    
    for i, doc in enumerate(docs, 1):
        print(f"[{i}] Источник: {doc.metadata.get('source', 'unknown')}")
        print(f"    Чанк ID: {doc.metadata.get('chunk_id', 'unknown')}")
        print(f"    Размер: {doc.metadata.get('chunk_size', 'unknown')} символов")
        print(f"\n    Текст чанка:")
        print(f"    {doc.page_content[:300]}...")
        print()


def main():
    """Основная функция для тестирования поиска"""
    print("="*80)
    print("ТЕСТИРОВАНИЕ ПОИСКА ПО ВЕКТОРНОМУ ИНДЕКСУ")
    print("="*80)
    print()
    
    # Загружаем индекс
    vectorstore = load_index()
    
    # Тестовые запросы
    test_queries = [
        "Кто такой Xarn Velgor?",
        "Что такое Synth Flux?",
        "Где находится Desertia?",
        "Что такое Void Core?",
        "Кто такие Aether Knights?"
    ]
    
    # Тестируем каждый запрос
    for query in test_queries:
        test_query(vectorstore, query, k=3)
        print()


if __name__ == "__main__":
    main()

