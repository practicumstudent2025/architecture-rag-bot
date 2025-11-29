"""
Модуль для создания промптов с Few-shot и Chain-of-Thought
"""
from typing import List, Optional
from langchain.schema import Document
from rag_bot.security import sanitize_content


# Предопределенные вопросы для Few-shot примеров (из той же предметной области)
FEW_SHOT_QUESTIONS = [
    "Кто такой Xarn Velgor?",
    "Что такое Synth Flux?"
]


def create_system_prompt() -> str:
    """
    Создает системный промпт с Chain-of-Thought инструкциями
    
    Returns:
        str: Системный промпт
    """
    return """Ты помощник, который отвечает на вопросы на основе предоставленной базы знаний.

При ответе на вопрос:
- Дай естественный, связный ответ своими словами
- Используй информацию из предоставленных документов
- Избегай формальных шаблонов типа "1. Сначала... 2. В документе... 3. Следовательно..."
- Не упоминай технические пометки типа "↑ 285.0" - используй только содержательную информацию
- Отвечай так, как будто ты знаешь эту информацию, а не цитируешь документы
- Если информации недостаточно, просто скажи "Я не знаю" без лишних объяснений

Пример хорошего ответа:
"HyperRelay использует технологию VoidCore в качестве источника питания."

Пример плохого ответа:
"1. Сначала найду информацию. 2. В документе указано... 3. Следовательно..."

Если информации недостаточно для ответа, просто скажи "Я не знаю"."""


def extract_few_shot_examples(vectorstore, questions: List[str]) -> List[dict]:
    """
    Извлекает Few-shot примеры из векторной базы знаний
    
    Args:
        vectorstore: Векторное хранилище
        questions: Список вопросов для поиска примеров
        
    Returns:
        List[dict]: Список примеров с вопросами и ответами из базы
    """
    examples = []
    for question in questions:
        # Ищем релевантные чанки для каждого вопроса
        docs = vectorstore.similarity_search(question, k=1)
        if docs:
            # Формируем естественный ответ на основе найденного чанка
            content = docs[0].page_content.strip()
            # Убираем технические пометки и берем содержательную часть
            lines = content.split('\n')
            clean_lines = []
            for line in lines:
                # Пропускаем строки с техническими пометками
                if not (line.strip().startswith('↑') or line.strip().startswith('[') or len(line.strip()) < 10):
                    clean_lines.append(line.strip())
            
            # Берем первые 2-3 содержательные строки
            clean_content = ' '.join(clean_lines[:3])
            if len(clean_content) > 250:
                clean_content = clean_content[:250] + "..."
            
            examples.append({
                "question": question,
                "answer": clean_content if clean_content else content[:200]
            })
    return examples


def create_few_shot_prompt(vectorstore=None) -> str:
    """
    Создает Few-shot промпт с примерами из базы знаний
    
    Args:
        vectorstore: Векторное хранилище (опционально, для извлечения примеров)
        
    Returns:
        str: Few-shot промпт
    """
    # Если vectorstore передан, извлекаем примеры из базы
    if vectorstore:
        examples = extract_few_shot_examples(vectorstore, FEW_SHOT_QUESTIONS)
    else:
        # Fallback на статические примеры (для обратной совместимости)
        examples = [
            {
                "question": "Кто такой Xarn Velgor?",
                "answer": "Xarn Velgor - это могущественный воин, который был известен своими способностями в использовании Synth Flux."
            },
            {
                "question": "Что такое Synth Flux?",
                "answer": "Synth Flux - это энергетическое поле, созданное всей жизнью, которое связывает все во вселенной вместе."
            }
        ]
    
    examples_text = "\n\n".join([
        f"Q: {ex['question']}\nA: {ex['answer']}"
        for ex in examples
    ])
    
    return f"""Примеры ответов:

{examples_text}

Ответь на вопрос естественно и связно:"""


def create_rag_prompt(query: str, context_docs: List[Document], vectorstore=None) -> str:
    """
    Создает финальный RAG промпт с контекстом
    
    Args:
        query: Пользовательский запрос
        context_docs: Релевантные документы из векторной базы
        vectorstore: Векторное хранилище (опционально, для Few-shot примеров)
        
    Returns:
        str: Полный промпт для LLM
    """
    # Формируем контекст из найденных документов (с очисткой от вредоносного контента)
    context_parts = []
    for i, doc in enumerate(context_docs, 1):
        source = doc.metadata.get("source", "Неизвестный источник")
        content = sanitize_content(doc.page_content.strip())  # Очистка от инъекций
        context_parts.append(f"[Документ {i} из {source}]\n{content}")
    
    context = "\n\n".join(context_parts)
    
    # Собираем полный промпт с Few-shot примерами из базы
    few_shot = create_few_shot_prompt(vectorstore)
    
    prompt = f"""{few_shot}

Q: {query}

Контекст из базы знаний:
{context}

A: (Дай естественный, связный ответ своими словами на основе найденной информации. Не используй формальные шаблоны рассуждений.)"""
    
    return prompt

