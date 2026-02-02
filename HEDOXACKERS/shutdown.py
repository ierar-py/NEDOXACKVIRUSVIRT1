import keyboard
import os

def shutdown_pc():
    print("Завершение работы...")
    # Для Windows: /s - выключение, /t 1 - через 1 секунду
    os.system("shutdown /s /t 1")

# Установка сочетания клавиш, например Ctrl+Alt+S
keyboard.add_hotkey('ctrl+alt+del', shutdown_pc)

print("Скрипт запущен. Нажмите Ctrl+Alt+S для выключения.")
# Блокируем скрипт, чтобы он не закрывался
keyboard.wait()
