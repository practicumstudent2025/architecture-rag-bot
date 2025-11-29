"""
Скрипт для очистки HTML страниц и извлечения чистого текста

Этот скрипт обрабатывает HTML файлы, скачанные с Fandom Wiki, и извлекает из них
чистый текст без HTML разметки. Результат сохраняется в текстовые файлы для
дальнейшей обработки (замены терминов).

Процесс работы:
1. Читает HTML файлы из папки raw_pages/
2. Парсит HTML с помощью BeautifulSoup
3. Удаляет ненужные элементы (скрипты, стили, навигацию)
4. Извлекает основной контент статьи
5. Сохраняет очищенный текст в папку cleaned_texts/
"""
import os
from bs4 import BeautifulSoup
import json

# Папка с исходными HTML файлами (скачанные страницы)
INPUT_DIR = os.path.join("data", "raw", "pages")

# Папка для сохранения очищенных текстовых файлов
OUTPUT_DIR = os.path.join("data", "processed", "texts")

# Создаем выходную папку, если её нет
os.makedirs(OUTPUT_DIR, exist_ok=True)


def extract_text_from_html(html_content):
    """
    Извлекает основной текст из HTML страницы
    
    Args:
        html_content (str): HTML содержимое страницы
        
    Returns:
        str: Очищенный текст статьи или None, если не удалось извлечь
        
    Процесс извлечения:
    1. Парсит HTML с помощью BeautifulSoup
    2. Удаляет служебные элементы (скрипты, стили, навигацию)
    3. Находит основной контент статьи
    4. Извлекает заголовок и текст из параграфов
    5. Объединяет все части в один текст
    """
    # Парсим HTML с помощью BeautifulSoup
    # 'html.parser' - встроенный парсер Python, не требует дополнительных библиотек
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Удаляем ненужные элементы, которые не содержат полезного контента
    # Эти элементы обычно содержат только разметку, скрипты или служебную информацию
    for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
        element.decompose()  # Удаляем элемент из дерева DOM
    
    # Находим основной контент статьи
    # На Fandom Wiki основной контент обычно находится в div с классом 'mw-parser-output'
    main_content = soup.find('div', {'class': 'mw-parser-output'})
    
    # Если не нашли основной контент по классу, пробуем альтернативные варианты
    # Это нужно для совместимости с разными версиями HTML или другими сайтами
    if not main_content:
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
    
    if main_content:
        # Извлекаем заголовок страницы
        # Сначала ищем заголовок с классом 'page-header__title' (стандарт Fandom Wiki)
        title = soup.find('h1', {'class': 'page-header__title'})
        
        # Если не нашли, пробуем найти любой h1 или title
        if not title:
            title = soup.find('h1') or soup.find('title')
        
        # Получаем текст заголовка, убирая лишние пробелы
        # Если заголовок не найден, используем "Untitled"
        title_text = title.get_text(strip=True) if title else "Untitled"
        
        # Извлекаем текст из параграфов, заголовков и списков
        # Это основные элементы, содержащие текстовый контент статьи
        paragraphs = main_content.find_all(['p', 'h2', 'h3', 'li'])
        
        # Начинаем список частей текста с заголовка
        text_parts = [title_text]
        
        # Обрабатываем каждый найденный элемент
        for p in paragraphs:
            # Извлекаем текст из элемента, разделяя вложенные элементы пробелами
            # strip=True убирает пробелы в начале и конце
            text = p.get_text(separator=' ', strip=True)
            
            # Пропускаем слишком короткие фрагменты (менее 20 символов)
            # Это помогает отфильтровать пустые параграфы, навигационные элементы и т.д.
            if text and len(text) > 20:
                text_parts.append(text)
        
        # Объединяем все части текста двойными переносами строк
        # Это создает читаемую структуру с разделением между параграфами
        return '\n\n'.join(text_parts)
    
    # Если не удалось найти основной контент, возвращаем None
    return None


def clean_page(filename):
    """
    Очищает одну HTML страницу и сохраняет результат в текстовый файл
    
    Args:
        filename (str): Имя HTML файла для обработки (например, "Darth_Vader.html")
        
    Returns:
        str: Базовое имя обработанного файла (без расширения) или None при ошибке
        
    Процесс:
    1. Проверяет, что файл имеет расширение .html
    2. Читает HTML содержимое из файла
    3. Извлекает чистый текст с помощью extract_text_from_html()
    4. Сохраняет результат в текстовый файл с тем же именем, но расширением .txt
    """
    # Формируем полный путь к входному файлу
    input_path = os.path.join(INPUT_DIR, filename)
    
    # Проверяем, что файл имеет расширение .html
    # Пропускаем другие файлы (например, JSON файлы со списками)
    if not filename.endswith('.html'):
        return None
    
    try:
        # Читаем HTML содержимое из файла
        # Используем encoding='utf-8' для корректной обработки специальных символов
        with open(input_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Извлекаем чистый текст из HTML
        text = extract_text_from_html(html_content)
        
        # Если текст успешно извлечен, сохраняем его
        if text:
            # Убираем расширение .html из имени файла
            # Например: "Darth_Vader.html" -> "Darth_Vader"
            base_name = filename.replace('.html', '')
            
            # Формируем путь для сохранения текстового файла
            # Например: "cleaned_texts/Darth_Vader.txt"
            output_path = os.path.join(OUTPUT_DIR, f"{base_name}.txt")
            
            # Сохраняем очищенный текст в файл
            # Используем encoding='utf-8' для сохранения всех символов
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            # Возвращаем базовое имя файла для дальнейшего использования
            return base_name
    except Exception as e:
        # Обрабатываем возможные ошибки (файл не найден, проблемы с кодировкой и т.д.)
        print(f"Ошибка при обработке {filename}: {e}")
    
    # Возвращаем None, если обработка не удалась
    return None


def main():
    """
    Основная функция для очистки всех HTML страниц
    
    Процесс работы:
    1. Получает список всех HTML файлов из папки raw_pages/
    2. Обрабатывает каждый файл с помощью clean_page()
    3. Собирает список успешно обработанных файлов
    4. Сохраняет список в JSON файл для отслеживания прогресса
    5. Выводит статистику обработки
    """
    # Получаем список всех HTML файлов из входной папки
    # Используем list comprehension для фильтрации только .html файлов
    html_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.html')]
    
    # Список для хранения имен успешно обработанных файлов
    cleaned = []
    
    # Обрабатываем каждый HTML файл
    for filename in html_files:
        # Очищаем страницу и получаем базовое имя файла
        result = clean_page(filename)
        
        # Если обработка успешна (result не None), добавляем в список
        if result:
            cleaned.append(result)
            # Выводим информацию о прогрессе обработки
            print(f"Очищено: {filename} -> {result}.txt")
    
    # Сохраняем список очищенных файлов в JSON файл
    # Это полезно для отслеживания прогресса и дальнейшей обработки
    cleaned_files_path = os.path.join(OUTPUT_DIR, "cleaned_files.json")
    with open(cleaned_files_path, 'w', encoding='utf-8') as f:
        # ensure_ascii=False позволяет сохранять Unicode символы как есть
        # indent=2 делает JSON файл читаемым с отступами
        json.dump(cleaned, f, ensure_ascii=False, indent=2)
    
    # Выводим итоговую статистику обработки
    # Показывает количество успешно обработанных файлов из общего числа
    print(f"\nОчищено файлов: {len(cleaned)}/{len(html_files)}")


if __name__ == "__main__":
    main()

