"""
Основной модуль RAG-пайплайна
"""
from typing import Optional, Tuple
from langchain.schema import Document
from rag_bot.vector_store import load_vector_store, search_relevant_chunks, search_relevant_chunks_with_scores
from rag_bot.llm_providers import get_llm_provider, LLMProvider
from rag_bot.prompts import create_system_prompt, create_rag_prompt
from rag_bot.security import create_secure_system_prompt, filter_malicious_chunks
from rag_bot.config import SEARCH_K, SIMILARITY_THRESHOLD


class RAGBot:
    """RAG-бот для работы с базой знаний"""
    
    def __init__(self):
        """Инициализация бота"""
        print("Загрузка векторного хранилища...")
        self.vectorstore = load_vector_store()
        print("Инициализация LLM провайдера...")
        self.llm = get_llm_provider()
        base_prompt = create_system_prompt()
        self.system_prompt = create_secure_system_prompt(base_prompt)  # Защищенный промпт
        print("RAG-бот готов к работе!")
    
    def _check_relevance(self, query: str, docs: list) -> Tuple[bool, float]:
        """
        Проверяет релевантность найденных документов
        
        Args:
            query: Поисковый запрос
            docs: Найденные документы
            
        Returns:
            Tuple[bool, float]: (релевантны ли документы, средний score)
        """
        if not docs:
            return False, 0.0
        
        # Используем similarity_search_with_score для получения оценок
        results = search_relevant_chunks_with_scores(self.vectorstore, query, k=SEARCH_K)
        
        if not results:
            return False, 0.0
        
        # Извлекаем scores (для ChromaDB: чем меньше расстояние, тем лучше)
        # Нормализуем в диапазон 0-1 (чем ближе к 0 расстояние, тем выше релевантность)
        scores = []
        for doc, distance in results:
            # Для косинусного расстояния: 1 - distance дает релевантность
            # Для евклидова: нормализуем через exp(-distance)
            relevance = 1.0 - min(distance, 1.0) if distance <= 1.0 else 1.0 / (1.0 + distance)
            scores.append(relevance)
        
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        # Проверяем порог релевантности
        is_relevant = avg_score >= SIMILARITY_THRESHOLD
        
        return is_relevant, avg_score
    
    def answer(self, query: str) -> str:
        """
        Генерирует ответ на вопрос пользователя
        
        Args:
            query: Вопрос пользователя
            
        Returns:
            str: Ответ бота
        """
        # 1. Поиск релевантных чанков
        relevant_docs = search_relevant_chunks(self.vectorstore, query, k=SEARCH_K)
        
        # 1.5. Фильтрация вредоносных чанков (Post-проверка)
        relevant_docs = filter_malicious_chunks(relevant_docs)
        
        # 2. Проверка релевантности (для случаев "Я не знаю")
        if not relevant_docs:
            return "Я не знаю ответ на этот вопрос. В базе знаний не найдено релевантной информации."
        
        is_relevant, score = self._check_relevance(query, relevant_docs)
        
        if not is_relevant:
            return f"Я не знаю ответ на этот вопрос. Найденная информация недостаточно релевантна (релевантность: {score:.2f}). Попробуйте переформулировать вопрос или уточнить детали."
        
        # 3. Создание промпта с Few-shot и контекстом (примеры извлекаются из базы)
        rag_prompt = create_rag_prompt(query, relevant_docs, self.vectorstore)
        
        # 4. Генерация ответа через LLM
        try:
            answer = self.llm.generate(rag_prompt, self.system_prompt)
            
            # Проверяем, не ответил ли LLM "не знаю"
            if any(phrase in answer.lower() for phrase in ["не знаю", "не могу", "нет информации", "не найдено"]):
                return f"Я не знаю ответ на этот вопрос. {answer}"
            
            return answer
        except Exception as e:
            return f"Произошла ошибка при генерации ответа: {str(e)}"
    
    def answer_with_sources(self, query: str) -> dict:
        """
        Генерирует ответ с указанием источников
        
        Args:
            query: Вопрос пользователя
            
        Returns:
            dict: Ответ и источники
        """
        relevant_docs = search_relevant_chunks(self.vectorstore, query, k=SEARCH_K)
        
        # Фильтрация вредоносных чанков (Post-проверка)
        relevant_docs = filter_malicious_chunks(relevant_docs)
        
        if not relevant_docs:
            return {
                "answer": "Я не знаю ответ на этот вопрос. В базе знаний не найдено релевантной информации.",
                "sources": []
            }
        
        is_relevant, score = self._check_relevance(query, relevant_docs)
        
        if not is_relevant:
            return {
                "answer": f"Я не знаю ответ на этот вопрос. Найденная информация недостаточно релевантна (релевантность: {score:.2f}). Попробуйте переформулировать вопрос или уточнить детали.",
                "sources": []
            }
        
        rag_prompt = create_rag_prompt(query, relevant_docs, self.vectorstore)
        
        try:
            answer = self.llm.generate(rag_prompt, self.system_prompt)
            sources = [doc.metadata.get("source", "Неизвестно") for doc in relevant_docs]
            
            # Проверяем, не ответил ли LLM "не знаю"
            if any(phrase in answer.lower() for phrase in ["не знаю", "не могу", "нет информации", "не найдено"]):
                answer = f"Я не знаю ответ на этот вопрос. {answer}"
            
            return {
                "answer": answer,
                "sources": sources
            }
        except Exception as e:
            return {
                "answer": f"Произошла ошибка при генерации ответа: {str(e)}",
                "sources": []
            }

