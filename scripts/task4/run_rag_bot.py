"""
Скрипт для запуска RAG-бота в консольном режиме
"""
from rag_bot.rag_pipeline import RAGBot


def main():
    """Основная функция для консольного режима"""
    print("=" * 80)
    print("RAG-БОТ: Консольный режим")
    print("=" * 80)
    print("Введите 'exit' или 'quit' для выхода\n")
    
    bot = RAGBot()
    
    while True:
        query = input("\nВаш вопрос: ").strip()
        
        if query.lower() in ['exit', 'quit', 'выход']:
            print("До свидания!")
            break
        
        if not query:
            continue
        
        print("\n" + "-" * 80)
        answer = bot.answer(query)
        print(answer)
        print("-" * 80)


if __name__ == "__main__":
    main()

