"""
Скрипт для замены терминов в текстах согласно словарю замен

Этот скрипт обрабатывает очищенные текстовые файлы и заменяет все упоминания
оригинальных терминов из вселенной Star Wars на вымышленные названия согласно
словарю замен. Также автоматически переименовывает файлы с новыми названиями.

Процесс работы:
1. Загружает словарь замен из terms_map.json
2. Читает очищенные тексты из папки cleaned_texts/
3. Заменяет все упоминания терминов в текстах
4. Определяет новые имена файлов на основе замен
5. Сохраняет обработанные тексты в knowledge_base/ с новыми именами
6. Копирует словарь замен в knowledge_base/

Примеры замен:
- "Darth Vader" → "Xarn Velgor"
- "Death Star" → "Void Core"
- "Jedi" → "Aether Knights"
"""
import os
import json
import re

# Папка с очищенными текстами (входные данные)
INPUT_DIR = os.path.join("data", "processed", "texts")

# Папка для сохранения обработанных текстов с замененными терминами
OUTPUT_DIR = os.path.join("data", "knowledge_base")

# Файл со словарем замен терминов
TERMS_MAP_FILE = os.path.join("config", "terms_map.json")

# Создаем выходную папку, если её нет
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_terms_map():
    """
    Загружает словарь замен из JSON файла и подготавливает его для использования
    
    Returns:
        tuple: (replacements, description)
            - replacements (dict): Отсортированный словарь замен {оригинал: замена}
            - description (str): Описание словаря замен
    
    Важно:
        Словарь сортируется по длине оригинальных терминов (от длинных к коротким).
        Это необходимо для корректной замены, чтобы избежать частичных замен.
        Например, "Darth Vader" должен заменяться раньше, чем "Vader".
    """
    # Читаем JSON файл со словарем замен
    # Используем encoding='utf-8' для корректной обработки специальных символов
    with open(TERMS_MAP_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Собираем все замены из разных категорий в один словарь
    # Это упрощает поиск и применение замен
    replacements = {}
    
    # Категории терминов в словаре замен
    # Каждая категория содержит словарь {оригинал: замена}
    for category in ['characters', 'organizations', 'locations', 'technologies', 'events', 'concepts']:
        if category in data:
            # Объединяем замены из текущей категории в общий словарь
            replacements.update(data[category])
    
    # Сортируем замены по длине оригинальных терминов (от длинных к коротким)
    # Это критически важно для корректной замены!
    # 
    # Пример проблемы без сортировки:
    # Если сначала заменить "Vader" на "Velgor", то "Darth Vader" станет "Darth Velgor"
    # и замена "Darth Vader" → "Xarn Velgor" не сработает
    #
    # С сортировкой:
    # Сначала заменяется "Darth Vader" → "Xarn Velgor"
    # Затем "Vader" (если остался) → "Velgor"
    sorted_replacements = sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True)
    
    # Преобразуем отсортированный список кортежей обратно в словарь
    # Возвращаем также описание словаря для информационных целей
    return dict(sorted_replacements), data.get('description', '')


def replace_terms_in_text(text, replacements):
    """
    Заменяет все термины в тексте согласно словарю замен
    
    Args:
        text (str): Исходный текст для обработки
        replacements (dict): Словарь замен {оригинал: замена}
        
    Returns:
        str: Текст с замененными терминами
    
    Процесс замены:
    1. Для каждой пары (оригинал, замена) из словаря
    2. Создает регулярные выражения для поиска термина
    3. Учитывает различные варианты написания (регистр)
    4. Заменяет все вхождения термина в тексте
    5. Использует границы слов (\b) для точного совпадения
    
    Важно:
        - Использует границы слов (\b) для избежания частичных замен
        - Учитывает регистр (заменяет с сохранением регистра)
        - Обрабатывает термины в порядке убывания длины (уже отсортированы)
    """
    # Начинаем с исходного текста
    result = text
    
    # Обрабатываем каждую пару (оригинал, замена) из словаря
    # Словарь уже отсортирован по длине (от длинных к коротким)
    for original, replacement in replacements.items():
        # Используем регулярное выражение для замены с учетом границ слов
        # \b - граница слова (word boundary), гарантирует точное совпадение
        # re.escape() - экранирует специальные символы в оригинальном термине
        
        # Создаем паттерны для различных вариантов написания:
        patterns = [
            # Оригинальный вариант (как в словаре)
            (r'\b' + re.escape(original) + r'\b', replacement),
            # Строчными буквами
            (r'\b' + re.escape(original.lower()) + r'\b', replacement.lower()),
            # С заглавной буквы (только первая буква)
            (r'\b' + re.escape(original.capitalize()) + r'\b', replacement.capitalize()),
        ]
        
        # Применяем каждый паттерн к тексту
        for pattern, repl in patterns:
            # re.sub() заменяет все вхождения паттерна на замену
            # flags=re.IGNORECASE делает поиск нечувствительным к регистру
            # Это позволяет находить термины в любом регистре
            result = re.sub(pattern, repl, result, flags=re.IGNORECASE)
    
    return result


def get_new_filename(old_filename, replacements):
    """
    Определяет новое имя файла на основе словаря замен
    
    Args:
        old_filename (str): Старое имя файла (например, "Darth_Vader.txt")
        replacements (dict): Словарь замен {оригинал: замена}
        
    Returns:
        str: Новое имя файла (например, "Xarn_Velgor.txt") или старое, если замена не найдена
    
    Процесс:
    1. Убирает расширение .txt из имени файла
    2. Преобразует подчеркивания и дефисы в пробелы для поиска
    3. Ищет соответствие в словаре замен
    4. Заменяет оригинальный термин на замененный в имени файла
    5. Возвращает новое имя с расширением .txt
    
    Примеры:
        "Darth_Vader.txt" → "Xarn_Velgor.txt"
        "Death_Star.txt" → "Void_Core.txt"
        "Obi-Wan_Kenobi.txt" → "Master_Valen.txt"
    """
    # Убираем расширение .txt из имени файла
    # Например: "Darth_Vader.txt" → "Darth_Vader"
    base_name = old_filename.replace('.txt', '')
    
    # Заменяем подчеркивания и дефисы на пробелы для поиска в словаре
    # В словаре термины хранятся с пробелами (например, "Darth Vader")
    # В именах файлов используются подчеркивания (например, "Darth_Vader")
    # или дефисы (например, "Obi-Wan_Kenobi")
    search_name = base_name.replace('_', ' ').replace('-', ' ')
    
    # Ищем соответствие в словаре замен
    # Словарь уже отсортирован по длине (от длинных к коротким)
    for original, replacement in replacements.items():
        # Преобразуем оригинальный термин в варианты с подчеркиваниями и дефисами
        # для поиска в имени файла
        original_underscore = original.replace(' ', '_')
        original_dash = original.replace(' ', '-')
        
        # Проверяем точное совпадение или начало имени файла с оригинальным термином
        # Это нужно для случаев, когда имя файла содержит несколько слов
        if search_name == original or search_name.startswith(original):
            # Заменяем оригинальный термин на замененный в имени файла
            # Учитываем варианты с подчеркиваниями и дефисами
            new_base = base_name.replace(original_underscore, replacement.replace(' ', '_'))
            new_base = new_base.replace(original_dash, replacement.replace(' ', '_'))
            return f"{new_base}.txt"
        
        # Если не нашли точное совпадение, пробуем найти частичное
        # Это нужно для случаев, когда имя файла содержит термин внутри другого текста
        if original_underscore in base_name:
            # Заменяем найденный термин на замененный
            new_base = base_name.replace(original_underscore, replacement.replace(' ', '_'))
            return f"{new_base}.txt"
        elif original_dash in base_name:
            # Аналогично для варианта с дефисом
            new_base = base_name.replace(original_dash, replacement.replace(' ', '_'))
            return f"{new_base}.txt"
    
    # Если не нашли замену, возвращаем старое имя файла
    # Это может быть нормально, если файл не содержит терминов из словаря
    return old_filename


def process_file(filename, replacements):
    """
    Обрабатывает один файл: заменяет термины в тексте и переименовывает файл
    
    Args:
        filename (str): Имя файла для обработки (например, "Darth_Vader.txt")
        replacements (dict): Словарь замен {оригинал: замена}
        
    Returns:
        str: Новое имя обработанного файла или None при ошибке
    
    Процесс:
    1. Читает текст из файла в cleaned_texts/
    2. Заменяет все термины в тексте согласно словарю
    3. Определяет новое имя файла на основе замен
    4. Сохраняет обработанный текст в knowledge_base/ с новым именем
    5. Выводит информацию о прогрессе
    """
    # Формируем полный путь к входному файлу
    input_path = os.path.join(INPUT_DIR, filename)
    
    # Проверяем, что файл имеет расширение .txt
    # Пропускаем другие файлы (например, JSON файлы со списками)
    if not filename.endswith('.txt'):
        return None
    
    try:
        # Читаем текст из файла
        # Используем encoding='utf-8' для корректной обработки специальных символов
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Заменяем все термины в тексте согласно словарю замен
        # Функция обрабатывает все вхождения терминов с учетом регистра
        replaced_text = replace_terms_in_text(text, replacements)
        
        # Определяем новое имя файла на основе словаря замен
        # Например: "Darth_Vader.txt" → "Xarn_Velgor.txt"
        new_filename = get_new_filename(filename, replacements)
        
        # Сохраняем обработанный текст в knowledge_base с новым именем
        output_path = os.path.join(OUTPUT_DIR, new_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(replaced_text)
        
        # Выводим информацию о прогрессе обработки
        # Если файл был переименован, указываем оба имени
        if new_filename != filename:
            print(f"Обработано и переименовано: {filename} → {new_filename}")
        else:
            print(f"Обработано: {filename}")
        
        # Возвращаем новое имя файла для дальнейшего использования
        return new_filename
    except Exception as e:
        # Обрабатываем возможные ошибки (файл не найден, проблемы с кодировкой и т.д.)
        print(f"Ошибка при обработке {filename}: {e}")
        return None


def main():
    """
    Основная функция для замены терминов во всех файлах
    
    Процесс работы:
    1. Загружает словарь замен из terms_map.json
    2. Получает список всех txt файлов в cleaned_texts/
    3. Обрабатывает каждый файл: заменяет термины и переименовывает
    4. Сохраняет словарь замен в knowledge_base/ для справки
    5. Выводит статистику обработки
    """
    # Загружаем словарь замен из JSON файла
    # replacements - отсортированный словарь всех замен
    # description - описание словаря для информационных целей
    replacements, description = load_terms_map()
    
    # Выводим информацию о загруженных заменах
    print(f"Загружено замен: {len(replacements)}")
    print(f"Описание: {description}\n")
    
    # Получаем список всех txt файлов из входной папки
    # Используем list comprehension для фильтрации только .txt файлов
    txt_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.txt')]
    
    # Список для хранения имен успешно обработанных файлов
    processed = []
    
    # Обрабатываем каждый файл
    for filename in txt_files:
        # Обрабатываем файл: заменяем термины и переименовываем
        result = process_file(filename, replacements)
        
        # Если обработка успешна (result не None), добавляем в список
        if result:
            processed.append(result)
            # Информация о прогрессе уже выводится в process_file()
            # Здесь можно добавить дополнительную обработку при необходимости
    
    # Сохраняем словарь замен в knowledge_base для справки
    # Это полезно для отслеживания всех примененных замен
    terms_output = os.path.join(OUTPUT_DIR, "terms_map.json")
    
    # Читаем исходный словарь замен
    with open(TERMS_MAP_FILE, 'r', encoding='utf-8') as f:
        terms_data = json.load(f)
    
    # Сохраняем копию словаря в knowledge_base
    with open(terms_output, 'w', encoding='utf-8') as f:
        # ensure_ascii=False позволяет сохранять Unicode символы как есть
        # indent=2 делает JSON файл читаемым с отступами
        json.dump(terms_data, f, ensure_ascii=False, indent=2)
    
    # Выводим итоговую статистику обработки
    # Показывает количество успешно обработанных файлов из общего числа
    print(f"\nОбработано файлов: {len(processed)}/{len(txt_files)}")
    print(f"Словарь замен сохранен в: {terms_output}")


if __name__ == "__main__":
    main()

