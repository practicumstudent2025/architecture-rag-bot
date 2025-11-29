"""
ШАГ 1: Загрузка документов из базы знаний
"""
import os
from pathlib import Path
from langchain.schema import Document
import json

KNOWLEDGE_BASE_DIR = os.path.join("data", "knowledge_base")
OUTPUT_DIR = "data/processed"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def main():
    print("="*80)
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
    
    # Сохраняем документы для следующего шага
    import pickle
    docs_path = os.path.join(OUTPUT_DIR, "documents.pkl")
    with open(docs_path, 'wb') as f:
        pickle.dump(documents, f)
    
    print(f"💾 Документы сохранены в: {docs_path}")
    
    return documents


if __name__ == "__main__":
    main()

