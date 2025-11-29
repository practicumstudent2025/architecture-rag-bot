"""
Переиндексация базы знаний с добавлением злонамеренного файла
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Определяем корневую директорию проекта
# Файл: scripts/task5/reindex_with_malicious.py
# Нужно подняться на 3 уровня: task5 -> scripts -> корень проекта
project_root = Path(__file__).parent.parent.parent.resolve()


class Tee:
    """Класс для дублирования вывода в консоль и файл"""
    def __init__(self, *files):
        self.files = files
    
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()
    
    def flush(self):
        for f in self.files:
            f.flush()


def main():
    # Определяем Python из виртуального окружения
    venv_python = project_root / ".venv" / "bin" / "python3"
    if venv_python.exists():
        python_executable = str(venv_python)
    else:
        # Fallback на системный Python
        python_executable = sys.executable
    
    # Создаем директорию для логов
    log_dir = project_root / "data" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Создаем файл лога с временной меткой
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"reindex_{timestamp}.log"
    
    # Открываем файл для записи
    log_file_handle = open(log_file, 'w', encoding='utf-8')
    
    # Сохраняем оригинальные stdout и stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    # Перенаправляем stdout и stderr в файл и консоль
    sys.stdout = Tee(sys.stdout, log_file_handle)
    sys.stderr = Tee(sys.stderr, log_file_handle)
    
    try:
        print("="*80)
        print("ПЕРЕИНДЕКСАЦИЯ БАЗЫ ЗНАНИЙ С ЗЛОНАМЕРЕННЫМ ФАЙЛОМ")
        print("="*80)
        print(f"Рабочая директория: {project_root}")
        print(f"Лог сохраняется в: {log_file}\n")
        
        # Удаляем старый индекс
        index_dir = project_root / "data" / "vector_index"
        if index_dir.exists():
            print(f"⚠️  Удаление старого индекса из {index_dir}...")
            shutil.rmtree(index_dir)
            print("✅ Старый индекс удален")
        
        # Удаляем промежуточные файлы
        processed_dir = project_root / "data" / "processed"
        if processed_dir.exists():
            print(f"⚠️  Очистка промежуточных файлов из {processed_dir}...")
            shutil.rmtree(processed_dir)
            print("✅ Промежуточные файлы удалены")
        
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Запускаем шаги индексации
        steps = [
            ("ШАГ 1: Загрузка документов (включая злонамеренный файл)", "scripts/task3/step1_load_documents.py"),
            ("ШАГ 2: Разбиение на чанки", "scripts/task3/step2_split_chunks.py"),
            ("ШАГ 3: Создание эмбеддингов", "scripts/task3/step3_create_embeddings.py"),
            ("ШАГ 4: Создание векторного индекса", "scripts/task3/step4_create_index.py"),
        ]
        
        for step_name, script_path in steps:
            print("\n" + "="*80)
            print(step_name)
            print("="*80)
            
            # Абсолютный путь к скрипту
            script_abs_path = project_root / script_path
            
            if not script_abs_path.exists():
                print(f"❌ Файл не найден: {script_abs_path}")
                return
            
            # subprocess автоматически использует текущие sys.stdout и sys.stderr,
            # которые мы уже перенаправили через Tee
            result = subprocess.run(
                [python_executable, str(script_abs_path)],
                cwd=str(project_root)
            )
            
            if result.returncode != 0:
                print(f"\n❌ Ошибка при выполнении {script_path}")
                return
        
        print("\n" + "="*80)
        print("✅ ПЕРЕИНДЕКСАЦИЯ ЗАВЕРШЕНА")
        print("="*80)
        print("База знаний переиндексирована с включением злонамеренного файла.")
        print("Теперь можно запускать тесты безопасности:")
        print("  python3 scripts/task5/test_security.py")
        print(f"\n📄 Полный лог сохранен в: {log_file}")
    finally:
        # Восстанавливаем оригинальные stdout и stderr, закрываем файл
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        log_file_handle.close()


if __name__ == "__main__":
    main()

