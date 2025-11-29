"""
Скрипт для переименования файлов в knowledge_base согласно словарю замен

Этот скрипт переименовывает файлы в папке knowledge_base, заменяя оригинальные
названия из вселенной Star Wars на вымышленные названия согласно словарю замен.

Процесс работы:
1. Загружает словарь замен из terms_map.json
2. Находит все txt файлы в knowledge_base/
3. Создает маппинг старых имен на новые согласно словарю
4. Переименовывает файлы
5. Сохраняет информацию о переименовании в rename_info.json

Пример:
- Darth_Vader.txt → Xarn_Velgor.txt
- Death_Star.txt → Void_Core.txt
- Jedi.txt → Aether_Knights.txt
"""
import os
import json
import re

# Папка с базой знаний, где находятся файлы для переименования
KNOWLEDGE_BASE_DIR = os.path.join("data", "knowledge_base")

# Файл со словарем замен терминов
TERMS_MAP_FILE = os.path.join("config", "terms_map.json")


def load_terms_map():
    """
    Загружает словарь замен из JSON файла
    
    Returns:
        tuple: (replacements, terms_data)
            - replacements (dict): Словарь всех замен {оригинал: замена}
            - terms_data (dict): Полные данные из JSON файла
    
    Процесс:
    1. Читает JSON файл со словарем замен
    2. Собирает все замены из разных категорий в один словарь
    3. Возвращает словарь замен и полные данные
    """
    # Читаем JSON файл со словарем замен
    # Используем encoding='utf-8' для корректной обработки специальных символов
    with open(TERMS_MAP_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Собираем все замены из разных категорий в один словарь
    # Это упрощает поиск соответствий при переименовании файлов
    replacements = {}
    
    # Категории терминов в словаре замен
    # Каждая категория содержит словарь {оригинал: замена}
    for category in ['characters', 'organizations', 'locations', 'technologies', 'events', 'concepts']:
        if category in data:
            # Объединяем замены из текущей категории в общий словарь
            replacements.update(data[category])
    
    return replacements, data


def create_filename_mapping(replacements):
    """
    Создает маппинг старых имен файлов на новые согласно словарю замен
    
    Args:
        replacements (dict): Словарь замен {оригинал: замена}
        
    Returns:
        dict: Словарь {старое_имя: новое_имя}
        
    Процесс:
    1. Получает список всех txt файлов в knowledge_base
    2. Для каждого файла ищет соответствие в словаре замен
    3. Создает новое имя файла с замененными терминами
    4. Возвращает маппинг старых имен на новые
    """
    # Словарь для хранения маппинга старых имен на новые
    filename_mapping = {}
    
    # Получаем список всех txt файлов в папке knowledge_base
    # Используем list comprehension для фильтрации только .txt файлов
    files = [f for f in os.listdir(KNOWLEDGE_BASE_DIR) if f.endswith('.txt')]
    
    # Обрабатываем каждый файл
    for old_filename in files:
        # Убираем расширение .txt из имени файла
        # Например: "Darth_Vader.txt" -> "Darth_Vader"
        base_name = old_filename.replace('.txt', '')
        
        # Заменяем подчеркивания на пробелы для поиска в словаре
        # В словаре термины хранятся с пробелами (например, "Darth Vader")
        # В именах файлов используются подчеркивания (например, "Darth_Vader")
        search_name = base_name.replace('_', ' ')
        
        # Ищем соответствие в словаре замен
        new_name = None
        
        # Сначала пробуем найти точное совпадение
        for original, replacement in replacements.items():
            # Проверяем точное совпадение или начало имени файла с оригинальным термином
            # Это нужно для случаев, когда имя файла содержит несколько слов
            if search_name == original or search_name.startswith(original):
                # Заменяем оригинальный термин на замененный в имени файла
                # Учитываем, что в именах файлов используются подчеркивания, а в словаре - пробелы
                new_base = base_name.replace(original.replace(' ', '_'), replacement.replace(' ', '_'))
                # Также проверяем вариант с дефисами (например, "Obi-Wan_Kenobi")
                new_base = new_base.replace(original.replace(' ', '-'), replacement.replace(' ', '_'))
                new_name = new_base
                break
        
        # Если не нашли точного совпадения, пробуем найти частичное
        # Это нужно для случаев, когда имя файла содержит термин внутри другого текста
        if not new_name:
            for original, replacement in replacements.items():
                # Преобразуем оригинальный термин в варианты с подчеркиваниями и дефисами
                original_underscore = original.replace(' ', '_')
                original_dash = original.replace(' ', '-')
                
                # Проверяем, содержит ли имя файла оригинальный термин
                if original_underscore in base_name:
                    # Заменяем найденный термин на замененный
                    new_name = base_name.replace(original_underscore, replacement.replace(' ', '_'))
                    break
                elif original_dash in base_name:
                    # Аналогично для варианта с дефисом
                    new_name = base_name.replace(original_dash, replacement.replace(' ', '_'))
                    break
        
        # Если нашли новое имя и оно отличается от старого, добавляем в маппинг
        if new_name and new_name != base_name:
            filename_mapping[old_filename] = f"{new_name}.txt"
        else:
            # Если не нашли замену, выводим предупреждение
            # Это может быть нормально, если файл не содержит терминов из словаря
            print(f"Не найдена замена для: {old_filename}")
    
    return filename_mapping


def rename_files(filename_mapping):
    """
    Переименовывает файлы согласно маппингу старых имен на новые
    
    Args:
        filename_mapping (dict): Словарь {старое_имя: новое_имя}
        
    Returns:
        list: Список кортежей [(старое_имя, новое_имя), ...] успешно переименованных файлов
    
    Процесс:
    1. Для каждой пары (старое_имя, новое_имя) в маппинге
    2. Формирует полные пути к файлам
    3. Проверяет существование старого файла
    4. Переименовывает файл с помощью os.rename()
    5. Сохраняет информацию о переименовании
    """
    # Список для хранения информации об успешно переименованных файлах
    renamed = []
    
    # Обрабатываем каждую пару (старое_имя, новое_имя) из маппинга
    for old_name, new_name in filename_mapping.items():
        # Формируем полные пути к старому и новому файлу
        # os.path.join() корректно обрабатывает разделители путей для разных ОС
        old_path = os.path.join(KNOWLEDGE_BASE_DIR, old_name)
        new_path = os.path.join(KNOWLEDGE_BASE_DIR, new_name)
        
        # Проверяем, существует ли старый файл
        # Это важно, так как файл мог быть удален или перемещен между созданием маппинга и переименованием
        if os.path.exists(old_path):
            # Переименовываем файл
            # os.rename() атомарно переименовывает файл (или перемещает, если пути разные)
            os.rename(old_path, new_path)
            
            # Сохраняем информацию о переименовании
            renamed.append((old_name, new_name))
            
            # Выводим информацию о прогрессе
            print(f"Переименовано: {old_name} → {new_name}")
        else:
            # Если файл не найден, выводим предупреждение
            print(f"Файл не найден: {old_name}")
    
    return renamed


def main():
    """
    Основная функция для переименования файлов в knowledge_base
    
    Процесс работы:
    1. Загружает словарь замен из terms_map.json
    2. Создает маппинг старых имен файлов на новые
    3. Переименовывает файлы согласно маппингу
    4. Сохраняет информацию о переименовании в JSON файл
    5. Выводит статистику выполнения
    """
    # Загружаем словарь замен из JSON файла
    # replacements - словарь всех замен {оригинал: замена}
    # terms_data - полные данные из JSON файла (для возможного использования)
    replacements, terms_data = load_terms_map()
    
    # Выводим информацию о загруженных заменах
    print(f"Загружено замен: {len(replacements)}\n")
    
    # Создаем маппинг старых имен файлов на новые
    # Функция анализирует все txt файлы в knowledge_base и находит соответствия в словаре замен
    filename_mapping = create_filename_mapping(replacements)
    
    # Выводим количество файлов, которые будут переименованы
    print(f"\nНайдено файлов для переименования: {len(filename_mapping)}\n")
    
    # Переименовываем файлы согласно маппингу
    # Функция возвращает список успешно переименованных файлов
    renamed = rename_files(filename_mapping)
    
    # Выводим статистику переименования
    # Показывает количество успешно переименованных файлов из общего числа
    print(f"\nПереименовано файлов: {len(renamed)}/{len(filename_mapping)}")
    
    # Сохраняем информацию о переименовании в JSON файл
    # Это полезно для отслеживания изменений и возможного отката
    rename_info = {
        "description": "Информация о переименовании файлов в knowledge_base",
        # Преобразуем список кортежей в словарь для удобства
        "renamed_files": {old: new for old, new in renamed}
    }
    
    # Сохраняем информацию о переименовании в JSON файл
    rename_info_path = os.path.join(KNOWLEDGE_BASE_DIR, "rename_info.json")
    with open(rename_info_path, 'w', encoding='utf-8') as f:
        # ensure_ascii=False позволяет сохранять Unicode символы как есть
        # indent=2 делает JSON файл читаемым с отступами
        json.dump(rename_info, f, ensure_ascii=False, indent=2)
    
    # Выводим информацию о сохранении отчета
    print(f"\nИнформация о переименовании сохранена в: {rename_info_path}")


if __name__ == "__main__":
    main()

