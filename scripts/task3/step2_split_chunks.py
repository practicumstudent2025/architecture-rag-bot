"""
ШАГ 2: Разбиение документов на чанки
"""
import os
import time
import pickle
from langchain.text_splitter import RecursiveCharacterTextSplitter

INPUT_DIR = "data/processed"
OUTPUT_DIR = "data/processed"
CHUNK_SIZE = 1000  # Размер чанка в символах
CHUNK_OVERLAP = 100  # Перекрытие между чанками


def main():
    print("="*80)
    print("ШАГ 2: РАЗБИЕНИЕ НА ЧАНКИ")
    print("="*80)
    
    # Загружаем документы из предыдущего шага
    docs_path = os.path.join(INPUT_DIR, "documents.pkl")
    if not os.path.exists(docs_path):
        print(f"❌ ОШИБКА: Файл {docs_path} не найден!")
        print("   Сначала запустите: python3 scripts/step1_load_documents.py")
        return
    
    print(f"Загрузка документов из {docs_path}...")
    with open(docs_path, 'rb') as f:
        documents = pickle.load(f)
    
    print(f"Загружено документов: {len(documents)}\n")
    
    # Создаем сплиттер
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
    
    # Сохраняем чанки для следующего шага
    chunks_path = os.path.join(OUTPUT_DIR, "chunks.pkl")
    with open(chunks_path, 'wb') as f:
        pickle.dump(chunks, f)
    
    print(f"💾 Чанки сохранены в: {chunks_path}")
    
    return chunks


if __name__ == "__main__":
    main()

