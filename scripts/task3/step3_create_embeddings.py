"""
ШАГ 3: Инициализация модели эмбеддингов
"""
import os
import time
from langchain_community.embeddings import HuggingFaceEmbeddings

EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-base"


def main():
    print("="*80)
    print("ШАГ 3: ИНИЦИАЛИЗАЦИЯ МОДЕЛИ ЭМБЕДДИНГОВ")
    print("="*80)
    
    print(f"Модель: {EMBEDDING_MODEL_NAME}")
    print(f"Репозиторий: https://huggingface.co/{EMBEDDING_MODEL_NAME}")
    print(f"Размер эмбеддингов: 768 измерений")
    print(f"\n⚠️  ВНИМАНИЕ: Загрузка модели может занять 1-2 минуты при первом запуске")
    print(f"   Модель будет скачана с Hugging Face Hub (~560 MB)")
    print(f"   Пожалуйста, не прерывайте процесс!\n")
    
    start_time = time.time()
    
    print("Загрузка модели...")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={'device': 'cpu'}
    )
    
    load_time = time.time() - start_time
    
    print(f"\n✅ Модель загружена успешно")
    print(f"⏱️  Время загрузки: {load_time:.2f} секунд")
    
    # Тестируем модель на простом примере
    print(f"\n🧪 Тестирование модели...")
    test_text = "Hello world"
    test_embedding = embeddings.embed_query(test_text)
    print(f"✅ Тест пройден: размер эмбеддинга = {len(test_embedding)} измерений")
    
    # Сохраняем информацию о модели
    model_info = {
        "name": EMBEDDING_MODEL_NAME,
        "repository": f"https://huggingface.co/{EMBEDDING_MODEL_NAME}",
        "embedding_dimension": 768,
        "load_time_seconds": round(load_time, 2)
    }
    
    import json
    info_path = "data/processed/model_info.json"
    os.makedirs("data/processed", exist_ok=True)
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(model_info, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Информация о модели сохранена в: {info_path}")
    print(f"\n✅ Шаг 3 завершен! Модель готова к использованию.")
    print(f"   Следующий шаг: python3 scripts/step4_create_index.py")


if __name__ == "__main__":
    main()

