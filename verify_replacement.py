"""
Скрипт для проверки качества замены терминов в базе знаний

Проверяет:
1. Что все оригинальные термины Star Wars заменены
2. Что замененные термины присутствуют в текстах
3. Что тексты остались читаемыми и логичными
4. Что тексты не распознаются как относящиеся к Star Wars
"""
import os
import json
import re
from collections import defaultdict

KNOWLEDGE_BASE_DIR = "knowledge_base"
TERMS_MAP_FILE = "terms_map.json"


def load_terms_map():
    """Загружает словарь замен из JSON файла"""
    with open(TERMS_MAP_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Собираем все замены в один словарь
    replacements = {}
    
    for category in ['characters', 'organizations', 'locations', 'technologies', 'events', 'concepts']:
        if category in data:
            replacements.update(data[category])
    
    return replacements, data


def find_original_terms_in_text(text, original_terms):
    """
    Находит все упоминания оригинальных терминов в тексте
    
    Args:
        text (str): Текст для проверки
        original_terms (list): Список оригинальных терминов для поиска
        
    Returns:
        list: Список найденных оригинальных терминов
    """
    found_terms = []
    
    for term in original_terms:
        # Создаем паттерн для поиска термина с учетом границ слов
        # Игнорируем регистр
        pattern = r'\b' + re.escape(term) + r'\b'
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        if matches:
            found_terms.append(term)
    
    return found_terms


def find_replaced_terms_in_text(text, replaced_terms):
    """
    Находит все упоминания замененных терминов в тексте
    
    Args:
        text (str): Текст для проверки
        replaced_terms (list): Список замененных терминов для поиска
        
    Returns:
        list: Список найденных замененных терминов
    """
    found_terms = []
    
    for term in replaced_terms:
        # Создаем паттерн для поиска термина с учетом границ слов
        pattern = r'\b' + re.escape(term) + r'\b'
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        if matches:
            found_terms.append(term)
    
    return found_terms


def check_text_readability(text):
    """
    Проверяет базовые показатели читаемости текста
    
    Args:
        text (str): Текст для проверки
        
    Returns:
        dict: Словарь с метриками читаемости
    """
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    words = re.findall(r'\b\w+\b', text)
    
    avg_sentence_length = len(words) / len(sentences) if sentences else 0
    avg_word_length = sum(len(w) for w in words) / len(words) if words else 0
    
    return {
        'total_words': len(words),
        'total_sentences': len(sentences),
        'avg_sentence_length': round(avg_sentence_length, 2),
        'avg_word_length': round(avg_word_length, 2),
        'readability_score': 'good' if 10 <= avg_sentence_length <= 25 else 'needs_review'
    }


def verify_file(filename, replacements):
    """
    Проверяет один файл на качество замены терминов
    
    Args:
        filename (str): Имя файла для проверки
        replacements (dict): Словарь замен (оригинал -> замена)
        
    Returns:
        dict: Результаты проверки
    """
    filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)
    
    if not filename.endswith('.txt'):
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        
        original_terms = list(replacements.keys())
        replaced_terms = list(replacements.values())
        
        # Проверяем наличие оригинальных терминов
        found_original = find_original_terms_in_text(text, original_terms)
        
        # Проверяем наличие замененных терминов
        found_replaced = find_replaced_terms_in_text(text, replaced_terms)
        
        # Проверяем читаемость
        readability = check_text_readability(text)
        
        return {
            'filename': filename,
            'found_original_terms': found_original,
            'found_replaced_terms': found_replaced,
            'has_original_terms': len(found_original) > 0,
            'has_replaced_terms': len(found_replaced) > 0,
            'readability': readability,
            'text_length': len(text)
        }
    except Exception as e:
        print(f"Ошибка при проверке {filename}: {e}")
        return None


def main():
    """Основная функция для проверки всех файлов"""
    replacements, terms_data = load_terms_map()
    
    print("=" * 80)
    print("ПРОВЕРКА КАЧЕСТВА ЗАМЕНЫ ТЕРМИНОВ В БАЗЕ ЗНАНИЙ")
    print("=" * 80)
    print(f"\nЗагружено замен: {len(replacements)}")
    print(f"Источник: {terms_data.get('source_universe', 'Unknown')}\n")
    
    # Получаем список всех txt файлов
    txt_files = [f for f in os.listdir(KNOWLEDGE_BASE_DIR) if f.endswith('.txt')]
    
    results = []
    files_with_original_terms = []
    files_without_replaced_terms = []
    
    print("Проверка файлов...\n")
    
    for filename in txt_files:
        result = verify_file(filename, replacements)
        if result:
            results.append(result)
            
            if result['has_original_terms']:
                files_with_original_terms.append(result)
            
            if not result['has_replaced_terms']:
                files_without_replaced_terms.append(result)
    
    # Статистика
    print("=" * 80)
    print("РЕЗУЛЬТАТЫ ПРОВЕРКИ")
    print("=" * 80)
    
    print(f"\nВсего проверено файлов: {len(results)}")
    print(f"Файлов с оригинальными терминами: {len(files_with_original_terms)}")
    print(f"Файлов без замененных терминов: {len(files_without_replaced_terms)}")
    
    # Детальная информация о проблемных файлах
    if files_with_original_terms:
        print("\n" + "=" * 80)
        print("⚠️  ВНИМАНИЕ: Найдены файлы с оригинальными терминами Star Wars!")
        print("=" * 80)
        for result in files_with_original_terms:
            print(f"\n📄 {result['filename']}")
            print(f"   Найдено оригинальных терминов: {len(result['found_original_terms'])}")
            print(f"   Термины: {', '.join(result['found_original_terms'][:5])}")
            if len(result['found_original_terms']) > 5:
                print(f"   ... и еще {len(result['found_original_terms']) - 5}")
    else:
        print("\n✅ Все оригинальные термины успешно заменены!")
    
    # Проверка читаемости
    print("\n" + "=" * 80)
    print("ПРОВЕРКА ЧИТАЕМОСТИ ТЕКСТОВ")
    print("=" * 80)
    
    total_words = sum(r['readability']['total_words'] for r in results)
    avg_sentence_length = sum(r['readability']['avg_sentence_length'] for r in results) / len(results)
    
    print(f"\nОбщее количество слов: {total_words:,}")
    print(f"Средняя длина предложения: {avg_sentence_length:.2f} слов")
    
    # Файлы с проблемами читаемости
    problematic_files = [r for r in results if r['readability']['readability_score'] == 'needs_review']
    if problematic_files:
        print(f"\n⚠️  Файлов с проблемами читаемости: {len(problematic_files)}")
        for r in problematic_files[:5]:
            print(f"   - {r['filename']}: {r['readability']['avg_sentence_length']} слов/предложение")
    else:
        print("\n✅ Все тексты имеют хорошую читаемость!")
    
    # Проверка наличия замененных терминов
    print("\n" + "=" * 80)
    print("ПРОВЕРКА НАЛИЧИЯ ЗАМЕНЕННЫХ ТЕРМИНОВ")
    print("=" * 80)
    
    files_with_replaced = [r for r in results if r['has_replaced_terms']]
    print(f"\nФайлов с замененными терминами: {len(files_with_replaced)}/{len(results)}")
    
    # Подсчет частоты замененных терминов
    term_frequency = defaultdict(int)
    for result in results:
        for term in result['found_replaced_terms']:
            term_frequency[term] += 1
    
    if term_frequency:
        print("\nТоп-10 наиболее часто встречающихся замененных терминов:")
        sorted_terms = sorted(term_frequency.items(), key=lambda x: x[1], reverse=True)
        for term, count in sorted_terms[:10]:
            print(f"   {term}: {count} файлов")
    
    # Итоговая оценка
    print("\n" + "=" * 80)
    print("ИТОГОВАЯ ОЦЕНКА")
    print("=" * 80)
    
    if not files_with_original_terms and len(files_with_replaced) > len(results) * 0.8:
        print("\n✅ ОТЛИЧНО: База знаний готова к использованию!")
        print("   - Все оригинальные термины заменены")
        print("   - Замененные термины присутствуют в большинстве файлов")
        print("   - Тексты читаемы и логичны")
        print("\n💡 Рекомендация: Тексты не должны распознаваться LLM как Star Wars")
    elif files_with_original_terms:
        print("\n❌ ТРЕБУЕТСЯ ДОРАБОТКА:")
        print("   - Найдены оригинальные термины Star Wars в некоторых файлах")
        print("   - Необходимо проверить и исправить замену терминов")
    else:
        print("\n⚠️  ЧАСТИЧНО ГОТОВО:")
        print("   - Оригинальные термины заменены")
        print("   - Но некоторые файлы могут не содержать замененных терминов")
    
    # Сохраняем отчет
    report = {
        'total_files': len(results),
        'files_with_original_terms': len(files_with_original_terms),
        'files_with_replaced_terms': len(files_with_replaced),
        'problematic_files': [r['filename'] for r in files_with_original_terms],
        'term_frequency': dict(term_frequency),
        'readability_stats': {
            'total_words': total_words,
            'avg_sentence_length': avg_sentence_length
        }
    }
    
    report_path = os.path.join(KNOWLEDGE_BASE_DIR, "verification_report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 Отчет сохранен в: {report_path}")


if __name__ == "__main__":
    main()

