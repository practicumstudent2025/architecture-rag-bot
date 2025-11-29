"""
Скрипт для переименования файлов в knowledge_base согласно словарю замен
"""
import os
import json
import re

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


def create_filename_mapping(replacements):
    """Создает маппинг старых имен файлов на новые"""
    filename_mapping = {}
    
    # Получаем список всех txt файлов в knowledge_base
    files = [f for f in os.listdir(KNOWLEDGE_BASE_DIR) if f.endswith('.txt')]
    
    for old_filename in files:
        # Убираем расширение .txt
        base_name = old_filename.replace('.txt', '')
        
        # Заменяем подчеркивания на пробелы для поиска в словаре
        search_name = base_name.replace('_', ' ')
        
        # Ищем соответствие в словаре замен
        new_name = None
        for original, replacement in replacements.items():
            # Проверяем точное совпадение или частичное
            if search_name == original or search_name.startswith(original):
                # Заменяем в имени файла
                new_base = base_name.replace(original.replace(' ', '_'), replacement.replace(' ', '_'))
                new_base = new_base.replace(original.replace(' ', '-'), replacement.replace(' ', '_'))
                new_name = new_base
                break
        
        # Если не нашли точного совпадения, пробуем найти частичное
        if not new_name:
            for original, replacement in replacements.items():
                # Проверяем, содержит ли имя файла оригинальный термин
                original_underscore = original.replace(' ', '_')
                original_dash = original.replace(' ', '-')
                
                if original_underscore in base_name:
                    new_name = base_name.replace(original_underscore, replacement.replace(' ', '_'))
                    break
                elif original_dash in base_name:
                    new_name = base_name.replace(original_dash, replacement.replace(' ', '_'))
                    break
        
        if new_name and new_name != base_name:
            filename_mapping[old_filename] = f"{new_name}.txt"
        else:
            # Если не нашли замену, оставляем старое имя
            print(f"Не найдена замена для: {old_filename}")
    
    return filename_mapping


def rename_files(filename_mapping):
    """Переименовывает файлы согласно маппингу"""
    renamed = []
    
    for old_name, new_name in filename_mapping.items():
        old_path = os.path.join(KNOWLEDGE_BASE_DIR, old_name)
        new_path = os.path.join(KNOWLEDGE_BASE_DIR, new_name)
        
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            renamed.append((old_name, new_name))
            print(f"Переименовано: {old_name} → {new_name}")
        else:
            print(f"Файл не найден: {old_name}")
    
    return renamed


def main():
    """Основная функция для переименования файлов"""
    replacements, terms_data = load_terms_map()
    
    print(f"Загружено замен: {len(replacements)}\n")
    
    # Создаем маппинг имен файлов
    filename_mapping = create_filename_mapping(replacements)
    
    print(f"\nНайдено файлов для переименования: {len(filename_mapping)}\n")
    
    # Переименовываем файлы
    renamed = rename_files(filename_mapping)
    
    print(f"\nПереименовано файлов: {len(renamed)}/{len(filename_mapping)}")
    
    # Сохраняем информацию о переименовании
    rename_info = {
        "description": "Информация о переименовании файлов в knowledge_base",
        "renamed_files": {old: new for old, new in renamed}
    }
    
    with open(os.path.join(KNOWLEDGE_BASE_DIR, "rename_info.json"), 'w', encoding='utf-8') as f:
        json.dump(rename_info, f, ensure_ascii=False, indent=2)
    
    print(f"\nИнформация о переименовании сохранена в: knowledge_base/rename_info.json")


if __name__ == "__main__":
    main()

