"""
Скрипт для замены терминов в текстах согласно словарю замен
"""
import os
import json
import re

INPUT_DIR = "cleaned_texts"
OUTPUT_DIR = "knowledge_base"
TERMS_MAP_FILE = "terms_map.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_terms_map():
    """Загружает словарь замен из JSON файла"""
    with open(TERMS_MAP_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Собираем все замены в один словарь
    replacements = {}
    
    for category in ['characters', 'organizations', 'locations', 'technologies', 'events', 'concepts']:
        if category in data:
            replacements.update(data[category])
    
    # Сортируем по длине (сначала длинные, чтобы избежать частичных замен)
    sorted_replacements = sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True)
    
    return dict(sorted_replacements), data.get('description', '')


def replace_terms_in_text(text, replacements):
    """Заменяет все термины в тексте согласно словарю"""
    result = text
    
    for original, replacement in replacements.items():
        # Используем регулярное выражение для замены с учетом границ слов
        # Учитываем различные варианты написания (с заглавной, строчной, множественное число)
        patterns = [
            (r'\b' + re.escape(original) + r'\b', replacement),
            (r'\b' + re.escape(original.lower()) + r'\b', replacement.lower()),
            (r'\b' + re.escape(original.capitalize()) + r'\b', replacement.capitalize()),
        ]
        
        for pattern, repl in patterns:
            result = re.sub(pattern, repl, result, flags=re.IGNORECASE)
    
    return result


def get_new_filename(old_filename, replacements):
    """Определяет новое имя файла на основе словаря замен"""
    base_name = old_filename.replace('.txt', '')
    
    # Заменяем подчеркивания и дефисы на пробелы для поиска
    search_name = base_name.replace('_', ' ').replace('-', ' ')
    
    # Ищем соответствие в словаре замен
    for original, replacement in replacements.items():
        original_underscore = original.replace(' ', '_')
        original_dash = original.replace(' ', '-')
        
        # Проверяем точное совпадение
        if search_name == original or search_name.startswith(original):
            new_base = base_name.replace(original_underscore, replacement.replace(' ', '_'))
            new_base = new_base.replace(original_dash, replacement.replace(' ', '_'))
            return f"{new_base}.txt"
        
        # Проверяем частичное совпадение
        if original_underscore in base_name:
            new_base = base_name.replace(original_underscore, replacement.replace(' ', '_'))
            return f"{new_base}.txt"
        elif original_dash in base_name:
            new_base = base_name.replace(original_dash, replacement.replace(' ', '_'))
            return f"{new_base}.txt"
    
    # Если не нашли замену, возвращаем старое имя
    return old_filename


def process_file(filename, replacements):
    """Обрабатывает один файл"""
    input_path = os.path.join(INPUT_DIR, filename)
    
    if not filename.endswith('.txt'):
        return None
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Заменяем термины
        replaced_text = replace_terms_in_text(text, replacements)
        
        # Определяем новое имя файла
        new_filename = get_new_filename(filename, replacements)
        
        # Сохраняем в knowledge_base с новым именем
        output_path = os.path.join(OUTPUT_DIR, new_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(replaced_text)
        
        if new_filename != filename:
            print(f"Обработано и переименовано: {filename} → {new_filename}")
        else:
            print(f"Обработано: {filename}")
        
        return new_filename
    except Exception as e:
        print(f"Ошибка при обработке {filename}: {e}")
        return None


def main():
    """Основная функция для замены терминов во всех файлах"""
    replacements, description = load_terms_map()
    
    print(f"Загружено замен: {len(replacements)}")
    print(f"Описание: {description}\n")
    
    txt_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.txt')]
    processed = []
    
    for filename in txt_files:
        result = process_file(filename, replacements)
        if result:
            processed.append(result)
            print(f"Обработано: {filename}")
    
    # Сохраняем словарь замен в knowledge_base
    terms_output = os.path.join(OUTPUT_DIR, "terms_map.json")
    with open(TERMS_MAP_FILE, 'r', encoding='utf-8') as f:
        terms_data = json.load(f)
    
    with open(terms_output, 'w', encoding='utf-8') as f:
        json.dump(terms_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nОбработано файлов: {len(processed)}/{len(txt_files)}")
    print(f"Словарь замен сохранен в: {terms_output}")


if __name__ == "__main__":
    main()

