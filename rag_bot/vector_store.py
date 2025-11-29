"""
Модуль для работы с векторным хранилищем
"""
import warnings
from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from rag_bot.config import VECTOR_INDEX_DIR, EMBEDDING_MODEL_NAME

# Подавляем deprecation warnings (классы все еще работают)
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain")


def load_vector_store():
    """
    Загружает векторное хранилище из сохраненного индекса
    
    Returns:
        Chroma: Векторное хранилище
    """
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={'device': 'cpu'}
    )
    
    vectorstore = Chroma(
        persist_directory=str(VECTOR_INDEX_DIR),
        embedding_function=embeddings
    )
    
    return vectorstore


def search_relevant_chunks(vectorstore, query, k=3):
    """
    Ищет релевантные чанки по запросу
    
    Args:
        vectorstore: Векторное хранилище
        query: Поисковый запрос
        k: Количество чанков для возврата
        
    Returns:
        list: Список релевантных документов
    """
    docs = vectorstore.similarity_search(query, k=k)
    return docs


def search_relevant_chunks_with_scores(vectorstore, query, k=3):
    """
    Ищет релевантные чанки по запросу с оценками релевантности
    
    Args:
        vectorstore: Векторное хранилище
        query: Поисковый запрос
        k: Количество чанков для возврата
        
    Returns:
        list: Список кортежей (документ, оценка)
    """
    results = vectorstore.similarity_search_with_score(query, k=k)
    return results

