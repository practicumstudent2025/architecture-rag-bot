"""
Скрипт для очистки HTML страниц и извлечения чистого текста
"""
import os
from bs4 import BeautifulSoup
import json

INPUT_DIR = "raw_pages"
OUTPUT_DIR = "cleaned_texts"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def extract_text_from_html(html_content):
    """Извлекает основной текст из HTML страницы"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Удаляем ненужные элементы
    for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
        element.decompose()
    
    # Находим основной контент статьи
    main_content = soup.find('div', {'class': 'mw-parser-output'})
    if not main_content:
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
    
    if main_content:
        # Извлекаем заголовок
        title = soup.find('h1', {'class': 'page-header__title'})
        if not title:
            title = soup.find('h1') or soup.find('title')
        
        title_text = title.get_text(strip=True) if title else "Untitled"
        
        # Извлекаем текст из параграфов
        paragraphs = main_content.find_all(['p', 'h2', 'h3', 'li'])
        text_parts = [title_text]
        
        for p in paragraphs:
            text = p.get_text(separator=' ', strip=True)
            if text and len(text) > 20:  # Пропускаем слишком короткие фрагменты
                text_parts.append(text)
        
        return '\n\n'.join(text_parts)
    
    return None


def clean_page(filename):
    """Очищает одну страницу"""
    input_path = os.path.join(INPUT_DIR, filename)
    
    if not filename.endswith('.html'):
        return None
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        text = extract_text_from_html(html_content)
        
        if text:
            # Сохраняем как .txt файл
            base_name = filename.replace('.html', '')
            output_path = os.path.join(OUTPUT_DIR, f"{base_name}.txt")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            return base_name
    except Exception as e:
        print(f"Ошибка при обработке {filename}: {e}")
    
    return None


def main():
    """Основная функция для очистки всех страниц"""
    html_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.html')]
    cleaned = []
    
    for filename in html_files:
        result = clean_page(filename)
        if result:
            cleaned.append(result)
            print(f"Очищено: {filename} -> {result}.txt")
    
    # Сохраняем список очищенных файлов
    with open(os.path.join(OUTPUT_DIR, "cleaned_files.json"), 'w', encoding='utf-8') as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)
    
    print(f"\nОчищено файлов: {len(cleaned)}/{len(html_files)}")


if __name__ == "__main__":
    main()

