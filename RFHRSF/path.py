import subprocess
import os
import sys

def install_program(program_path):
    """
    Функция для установки программы по указанному пути
    
    Args:
        program_path (str): Полный путь к установочному файлу
    """
    
    # Проверяем существует ли файл
    if not os.path.exists(program_path):
        print(f"Ошибка: Файл {program_path} не найден!")
        return False
    
    # Проверяем расширение файла
    file_extension = os.path.splitext(program_path)[1].lower()
    
    try:
        if file_extension == '.exe':
            # Для EXE файлов
            print(f"Запуск установки: {program_path}")
            # /S - тихая установка для многих инсталляторов
            # /silent - альтернативный параметр
            result = subprocess.run([program_path, '/S', '/verysilent'], 
                                  capture_output=True, text=True)
            
        elif file_extension == '.msi':
            # Для MSI файлов
            print(f"Запуск установки MSI: {program_path}")
            result = subprocess.run(['msiexec', '/i', program_path, '/quiet', '/norestart'],
                                  capture_output=True, text=True)
        else:
            print(f"Неподдерживаемый формат файла: {file_extension}")
            return False
        
        if result.returncode == 0:
            print("Программа успешно установлена!")
            return True
        else:
            print(f"Ошибка при установке. Код ошибки: {result.returncode}")
            print(f"Детали ошибки: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        return False

# Укажите путь к вашей программе здесь
program_path = r"C:\Windows\System32\drivers\f.exe"  # Замените на ваш путь

# Запуск установки
if __name__ == "__main__":
    install_program(program_path)
