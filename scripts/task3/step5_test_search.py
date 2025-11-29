"""
ШАГ 5: Тестирование поиска по векторному индексу
"""
import os
import json
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

INDEX_DIR = os.path.join("data", "vector_index")
EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-base"


def main():
    print("="*80)
    print("ШАГ 5: ТЕСТИРОВАНИЕ ПОИСКА")
    print("="*80)
    
    if not os.path.exists(INDEX_DIR):
        print(f"❌ ОШИБКА: Индекс не найден в {INDEX_DIR}")
        print("   Сначала запустите: python3 scripts/step4_create_index.py")
        return
    
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
    
    print("✅ Индекс загружен успешно\n")
    
    # Тестовые запросы
    test_queries = [
        "Кто такой Xarn Velgor?",
        "Что такое Synth Flux?",
        "Где находится Desertia?"
    ]
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Запрос: {query}")
        print("-" * 80)
        
        import time
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
    
    # Сохраняем результаты
    test_results_path = os.path.join(INDEX_DIR, "test_results.json")
    with open(test_results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Результаты тестирования сохранены в: {test_results_path}")
    print(f"\n✅ Шаг 5 завершен! Поиск работает корректно.")


if __name__ == "__main__":
    main()

