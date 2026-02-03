import keyboard
import subprocess

# Укажите путь к программе, которую хотите открыть
# Для Windows используйте двойные слэши или r'path'
APP_PATH = r'C:\Windows\System32\drivers\BSOD.exe' 

def open_app():
    try:
        # Открывает программу в новом процессе
        subprocess.Popen(APP_PATH)
        print("Программа открыта")
    except Exception as e:
        print(f"Ошибка: {e}")

# Настройка горячей клавиши (например, Ctrl+Alt+N)
keyboard.add_hotkey('ctrl+alt+del', open_app)

print("Скрипт запущен. Нажмите Ctrl+Alt+N для открытия...")
# Блокирует выполнение программы, ожидая нажатия
keyboard.wait()
