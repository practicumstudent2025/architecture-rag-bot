"""
ШАГ 4: Создание векторного индекса в ChromaDB
"""
import os
import time
import pickle
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

INPUT_DIR = "data/processed"
INDEX_DIR = os.path.join("data", "vector_index")
EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-base"


def main():
    print("="*80)
    print("ШАГ 4: СОЗДАНИЕ ВЕКТОРНОГО ИНДЕКСА")
    print("="*80)
    
    # Загружаем чанки из предыдущего шага
    chunks_path = os.path.join(INPUT_DIR, "chunks.pkl")
    if not os.path.exists(chunks_path):
        print(f"❌ ОШИБКА: Файл {chunks_path} не найден!")
        print("   Сначала запустите: python3 scripts/step2_split_chunks.py")
        return
    
    print(f"Загрузка чанков из {chunks_path}...")
    with open(chunks_path, 'rb') as f:
        chunks = pickle.load(f)
    
    print(f"Загружено чанков: {len(chunks):,}\n")
    
    # Загружаем модель эмбеддингов
    print("Загрузка модели эмбеддингов...")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={'device': 'cpu'}
    )
    print("✅ Модель загружена\n")
    
    print(f"Векторная БД: ChromaDB")
    print(f"Директория индекса: {INDEX_DIR}")
    print(f"Количество чанков для индексации: {len(chunks):,}")
    print(f"\n⚠️  ВНИМАНИЕ: Генерация эмбеддингов может занять значительное время")
    print(f"   Оценка времени: ~{len(chunks) * 0.05:.0f}-{len(chunks) * 0.1:.0f} секунд")
    print(f"   (~0.05-0.1 сек на чанк, зависит от размера)")
    print(f"   Для {len(chunks):,} чанков это примерно {len(chunks) * 0.05 / 60:.1f}-{len(chunks) * 0.1 / 60:.1f} минут")
    print(f"   Пожалуйста, не прерывайте процесс!\n")
    
    start_time = time.time()
    
    print("Генерация эмбеддингов и создание индекса...")
    print("Это может занять несколько минут...\n")
    
    # Показываем прогресс каждые 1000 чанков
    print("Прогресс индексации:")
    
    # Создаем векторное хранилище
    # ChromaDB автоматически генерирует эмбеддинги для всех чанков
    os.makedirs(INDEX_DIR, exist_ok=True)
    
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=INDEX_DIR
    )
    
    index_time = time.time() - start_time
    
    print(f"\n✅ Индекс создан и сохранен")
    print(f"⏱️  Время создания индекса: {index_time:.2f} секунд ({index_time/60:.2f} минут)")
    print(f"📁 Индекс сохранен в: {INDEX_DIR}")
    
    # Сохраняем информацию
    import json
    info = {
        "chunks_count": len(chunks),
        "indexing_time_seconds": round(index_time, 2),
        "indexing_time_minutes": round(index_time / 60, 2),
        "index_path": INDEX_DIR
    }
    
    info_path = os.path.join(INDEX_DIR, "index_info.json")
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Информация об индексе сохранена в: {info_path}")
    print(f"\n✅ Шаг 4 завершен! Индекс готов.")
    print(f"   Следующий шаг: python3 scripts/step5_test_search.py")


if __name__ == "__main__":
    main()

