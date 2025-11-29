"""
Скрипт для скачивания страниц из Star Wars Fandom Wiki
"""
import requests
from bs4 import BeautifulSoup
import os
import time
import json
from urllib.parse import urljoin, urlparse

# Список ключевых страниц для скачивания (31 страница)
PAGES = [
    "Darth_Vader",
    "Luke_Skywalker",
    "Princess_Leia",
    "Han_Solo",
    "Obi-Wan_Kenobi",
    "Yoda",
    "Emperor_Palpatine",
    "Anakin_Skywalker",
    "R2-D2",
    "C-3PO",
    "Chewbacca",
    "Death_Star",
    "Millennium_Falcon",
    "Lightsaber",
    "The_Force",
    "Jedi",
    "Sith",
    "Tatooine",
    "Coruscant",
    "Naboo",
    "Endor",
    "Hoth",
    "Dagobah",
    "Alderaan",
    "Blaster",
    "X-wing",
    "TIE_Fighter",
    "Clone_Trooper",
    "Stormtrooper",
    "Rebel_Alliance",
    "Galactic_Empire"
]

BASE_URL = "https://starwars.fandom.com/wiki/"
OUTPUT_DIR = "raw_pages"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def download_page(page_name):
    """Скачивает страницу и возвращает HTML"""
    url = urljoin(BASE_URL, page_name)
    print(f"Скачиваю: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Ошибка при скачивании {page_name}: {e}")
        return None


def save_page(page_name, html_content):
    """Сохраняет HTML страницы в файл"""
    if html_content:
        filepath = os.path.join(OUTPUT_DIR, f"{page_name}.html")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Сохранено: {filepath}")
        return True
    return False


def main():
    """Основная функция для скачивания всех страниц"""
    downloaded = []
    
    for page_name in PAGES:
        html = download_page(page_name)
        if save_page(page_name, html):
            downloaded.append(page_name)
        time.sleep(1)  # Пауза между запросами
    
    # Сохраняем список скачанных страниц
    with open(os.path.join(OUTPUT_DIR, "downloaded_pages.json"), 'w', encoding='utf-8') as f:
        json.dump(downloaded, f, ensure_ascii=False, indent=2)
    
    print(f"\nСкачано страниц: {len(downloaded)}/{len(PAGES)}")


if __name__ == "__main__":
    main()
