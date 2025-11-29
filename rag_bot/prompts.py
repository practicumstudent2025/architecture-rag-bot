"""
Модуль для создания промптов с Few-shot и Chain-of-Thought
"""
from typing import List
from langchain.schema import Document


# Few-shot примеры (из базы знаний)
FEW_SHOT_EXAMPLES = [
    {
        "question": "Кто такой Xarn Velgor?",
        "answer": "Xarn Velgor - это могущественный воин, который был известен своими способностями в использовании Synth Flux. Он был одним из ключевых персонажей в истории Void Dominion."
    },
    {
        "question": "Что такое Synth Flux?",
        "answer": "Synth Flux - это энергетическое поле, созданное всей жизнью, которое связывает все во вселенной вместе. Это фундаментальная сила, которую используют Aether Knights и Shadow Lords."
    }
]


def create_system_prompt() -> str:
    """
    Создает системный промпт с Chain-of-Thought инструкциями
    
    Returns:
        str: Системный промпт
    """
    return """Ты помощник, который отвечает на вопросы на основе предоставленной базы знаний.

ВАЖНО: Всегда следуй этим шагам при ответе:

1. Сначала проанализируй вопрос пользователя
2. Изучи предоставленные фрагменты из базы знаний
3. Найди релевантную информацию
4. Объясни свои рассуждения перед ответом
5. Дай точный ответ на основе найденной информации

Если информации недостаточно для ответа, честно скажи "Я не знаю" и объясни почему.

Всегда пиши свои шаги рассуждения перед финальным ответом."""


def create_few_shot_prompt() -> str:
    """
    Создает Few-shot промпт с примерами
    
    Returns:
        str: Few-shot промпт
    """
    examples_text = "\n\n".join([
        f"Q: {ex['question']}\nA: {ex['answer']}"
        for ex in FEW_SHOT_EXAMPLES
    ])
    
    return f"""Вот примеры правильных ответов:

{examples_text}

Теперь ответь на следующий вопрос по тому же принципу:"""


def create_rag_prompt(query: str, context_docs: List[Document]) -> str:
    """
    Создает финальный RAG промпт с контекстом
    
    Args:
        query: Пользовательский запрос
        context_docs: Релевантные документы из векторной базы
        
    Returns:
        str: Полный промпт для LLM
    """
    # Формируем контекст из найденных документов
    context_parts = []
    for i, doc in enumerate(context_docs, 1):
        source = doc.metadata.get("source", "Неизвестный источник")
        content = doc.page_content.strip()
        context_parts.append(f"[Документ {i} из {source}]\n{content}")
    
    context = "\n\n".join(context_parts)
    
    # Собираем полный промпт
    few_shot = create_few_shot_prompt()
    
    prompt = f"""{few_shot}

Q: {query}

Контекст из базы знаний:
{context}

A: (Сначала объясни свои шаги рассуждения, затем дай ответ)"""
    
    return prompt

