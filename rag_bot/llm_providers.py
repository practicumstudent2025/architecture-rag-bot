"""
Модуль для работы с различными LLM провайдерами
"""
from typing import List, Dict
from rag_bot.config import (
    LLM_PROVIDER, OPENAI_API_KEY, OPENAI_MODEL,
    YANDEX_API_KEY, YANDEX_FOLDER_ID
)


class LLMProvider:
    """Базовый класс для LLM провайдеров"""
    
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """
        Генерирует ответ на основе промпта
        
        Args:
            prompt: Пользовательский промпт
            system_prompt: Системный промпт
            
        Returns:
            str: Сгенерированный ответ
        """
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    """Провайдер для OpenAI GPT"""
    
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY не установлен")
        from openai import OpenAI
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
    
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content


class YandexGPTProvider(LLMProvider):
    """Провайдер для YandexGPT"""
    
    def __init__(self):
        if not YANDEX_API_KEY or not YANDEX_FOLDER_ID:
            raise ValueError("YANDEX_API_KEY или YANDEX_FOLDER_ID не установлены")
        import requests
        self.requests = requests
        self.api_key = YANDEX_API_KEY
        self.folder_id = YANDEX_FOLDER_ID
        self.url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Формируем сообщения
        messages = []
        if system_prompt:
            messages.append({"role": "system", "text": system_prompt})
        messages.append({"role": "user", "text": prompt})
        
        data = {
            "modelUri": f"gpt://{self.folder_id}/yandexgpt/latest",
            "completionOptions": {
                "stream": False,
                "temperature": 0.7,
                "maxTokens": 2000
            },
            "messages": messages
        }
        
        try:
            response = self.requests.post(self.url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result["result"]["alternatives"][0]["message"]["text"]
        except self.requests.exceptions.HTTPError as e:
            error_detail = "Неизвестная ошибка"
            try:
                error_json = e.response.json()
                error_detail = error_json.get("message", str(error_json))
            except:
                error_detail = e.response.text or str(e)
            
            if e.response.status_code == 403:
                raise ValueError(
                    f"Ошибка 403 Forbidden при обращении к YandexGPT API.\n"
                    f"Детали: {error_detail}\n\n"
                    f"Проверьте:\n"
                    f"1. API ключ создан с scope: yc.ai.languageModels.execute\n"
                    f"2. Сервисному аккаунту назначена роль: ai.languageModels.user\n"
                    f"3. Роль назначена для правильного каталога (Folder ID: {self.folder_id})"
                )
            raise ValueError(f"Ошибка YandexGPT API ({e.response.status_code}): {error_detail}")


class LocalLLMProvider(LLMProvider):
    """Провайдер для локальной модели (Hugging Face)"""
    
    def __init__(self, model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct"):
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto" if self.device == "cuda" else None
        )
        if self.device == "cpu":
            self.model = self.model.to(self.device)
    
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        inputs = self.tokenizer(full_prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.7,
            do_sample=True
        )
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response[len(full_prompt):].strip()


def get_llm_provider() -> LLMProvider:
    """
    Возвращает LLM провайдер в зависимости от конфигурации
    
    Returns:
        LLMProvider: Экземпляр провайдера
    """
    if LLM_PROVIDER == "openai":
        return OpenAIProvider()
    elif LLM_PROVIDER == "yandex":
        return YandexGPTProvider()
    elif LLM_PROVIDER == "local":
        return LocalLLMProvider()
    else:
        raise ValueError(f"Неизвестный провайдер LLM: {LLM_PROVIDER}")

