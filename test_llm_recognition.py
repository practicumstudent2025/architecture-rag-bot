"""
Скрипт для проверки, что LLM не распознает тексты как относящиеся к Star Wars

Тестирует несколько документов из базы знаний, отправляя их в LLM
и проверяя, распознает ли модель вселенную Star Wars.
"""
import os
import json
import random

KNOWLEDGE_BASE_DIR = "knowledge_base"


def get_sample_text(filename, max_length=500):
    """
    Получает образец текста из файла
    
    Args:
        filename (str): Имя файла
        max_length (int): Максимальная длина образца в символах
        
    Returns:
        str: Образец текста
    """
    filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Берем первые max_length символов
        sample = text[:max_length]
        
        # Обрезаем до последнего пробела, чтобы не обрывать слово
        if len(text) > max_length:
            last_space = sample.rfind(' ')
            if last_space > 0:
                sample = sample[:last_space] + "..."
        
        return sample
    except Exception as e:
        print(f"Ошибка при чтении {filename}: {e}")
        return None


def create_test_prompt(text_sample):
    """
    Создает промпт для тестирования LLM
    
    Args:
        text_sample (str): Образец текста
        
    Returns:
        str: Промпт для LLM
    """
    prompt = f"""Прочитай следующий текст и ответь на вопросы:

{text_sample}

Вопросы:
1. К какой вселенной/франшизе относится этот текст? (Если не знаешь, напиши "Неизвестная вселенная")
2. Упоминаются ли в тексте персонажи или места из вселенной Star Wars? (Да/Нет)
3. Опиши кратко, о чем этот текст (1-2 предложения)

Ответь в формате JSON:
{{
    "universe": "название вселенной или 'Неизвестная вселенная'",
    "mentions_star_wars": true/false,
    "description": "краткое описание"
}}"""
    
    return prompt


def test_with_openai_api(text_sample, api_key=None):
    """
    Тестирует текст с помощью OpenAI API
    
    Args:
        text_sample (str): Образец текста
        api_key (str): API ключ OpenAI (опционально)
        
    Returns:
        dict: Результат тестирования
    """
    # Проверяем, установлен ли openai
    try:
        from openai import OpenAI
    except ImportError:
        print("⚠️  OpenAI не установлен. Установите: pip install openai")
        return None
    
    if not api_key:
        api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("⚠️  OPENAI_API_KEY не установлен. Пропускаем тест с OpenAI.")
        return None
    
    try:
        client = OpenAI(api_key=api_key)
        
        prompt = create_test_prompt(text_sample)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты помощник, который анализирует тексты и определяет, к какой вселенной они относятся."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        result_text = response.choices[0].message.content
        
        # Пытаемся распарсить JSON из ответа
        try:
            # Ищем JSON в ответе
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                result_json = json.loads(result_text[json_start:json_end])
                return result_json
        except:
            pass
        
        # Если не удалось распарсить, возвращаем текст ответа
        return {"raw_response": result_text}
        
    except Exception as e:
        print(f"Ошибка при вызове OpenAI API: {e}")
        return None


def manual_test(text_sample):
    """
    Ручной тест - выводит текст для проверки человеком
    
    Args:
        text_sample (str): Образец текста
    """
    print("\n" + "=" * 80)
    print("ОБРАЗЕЦ ТЕКСТА ДЛЯ РУЧНОЙ ПРОВЕРКИ")
    print("=" * 80)
    print(text_sample)
    print("\n" + "=" * 80)
    print("ВОПРОСЫ ДЛЯ ПРОВЕРКИ:")
    print("1. Упоминаются ли персонажи или места из Star Wars?")
    print("2. Можно ли понять, что это текст о Star Wars?")
    print("3. Текст логичен и читаем?")
    print("=" * 80)


def main():
    """Основная функция для тестирования"""
    print("=" * 80)
    print("ТЕСТИРОВАНИЕ РАСПОЗНАВАНИЯ LLM")
    print("=" * 80)
    print("\nЭтот скрипт проверяет, что LLM не распознает тексты как Star Wars")
    print("Выберите режим тестирования:\n")
    print("1. Ручная проверка (вывод образцов текстов)")
    print("2. Тест с OpenAI API (требует API ключ)")
    print("3. Оба варианта\n")
    
    # Получаем список файлов
    txt_files = [f for f in os.listdir(KNOWLEDGE_BASE_DIR) if f.endswith('.txt')]
    
    # Выбираем случайные файлы для тестирования
    sample_files = random.sample(txt_files, min(5, len(txt_files)))
    
    print(f"Выбрано файлов для тестирования: {len(sample_files)}")
    print(f"Файлы: {', '.join(sample_files)}\n")
    
    results = []
    
    for filename in sample_files:
        print(f"\n{'='*80}")
        print(f"Тестирование: {filename}")
        print(f"{'='*80}")
        
        text_sample = get_sample_text(filename, max_length=500)
        
        if not text_sample:
            continue
        
        # Ручная проверка
        manual_test(text_sample)
        
        # Тест с OpenAI (если доступен)
        api_result = test_with_openai_api(text_sample)
        
        if api_result:
            print("\nРезультат OpenAI API:")
            print(json.dumps(api_result, ensure_ascii=False, indent=2))
            
            # Проверяем, не распознал ли модель Star Wars
            if api_result.get('mentions_star_wars') == True:
                print("⚠️  ВНИМАНИЕ: Модель распознала упоминания Star Wars!")
            elif 'star wars' in str(api_result.get('universe', '')).lower():
                print("⚠️  ВНИМАНИЕ: Модель определила вселенную как Star Wars!")
            else:
                print("✅ Модель не распознала текст как Star Wars")
        
        results.append({
            'filename': filename,
            'api_result': api_result
        })
    
    # Сохраняем результаты
    report_path = os.path.join(KNOWLEDGE_BASE_DIR, "llm_test_report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 Отчет сохранен в: {report_path}")
    
    # Итоговая статистика
    print("\n" + "=" * 80)
    print("ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 80)
    
    recognized_as_sw = sum(1 for r in results 
                           if r.get('api_result', {}).get('mentions_star_wars') == True 
                           or 'star wars' in str(r.get('api_result', {}).get('universe', '')).lower())
    
    print(f"\nПротестировано файлов: {len(results)}")
    print(f"Распознано как Star Wars: {recognized_as_sw}")
    
    if recognized_as_sw == 0:
        print("\n✅ ОТЛИЧНО: Ни один текст не распознан как Star Wars!")
    else:
        print(f"\n⚠️  ВНИМАНИЕ: {recognized_as_sw} файлов распознаны как Star Wars")
        print("   Рекомендуется проверить замену терминов в этих файлах")


if __name__ == "__main__":
    main()

