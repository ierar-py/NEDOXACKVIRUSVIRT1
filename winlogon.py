import winreg
import os

# ===== УКАЖИТЕ ПУТЬ К ВАШЕМУ ФАЙЛУ ЗДЕСЬ =====
FILE_PATH = r"C:\Users\1\Desktop\RFHRSF\start.bat"  # ИЗМЕНИТЕ ЭТОТ ПУТЬ!
# ==============================================

def add_to_userinit_auto():
    """
    Автоматически добавляет файл в Userinit
    """
    print("=" * 50)
    print("ДОБАВЛЕНИЕ ФАЙЛА В WINLOGON USERINIT")
    print("=" * 50)
    print(f"Файл: {FILE_PATH}")
    
    # Проверяем существование файла
    if not os.path.exists(FILE_PATH):
        print(f"❌ ОШИБКА: Файл не найден!")
        print(f"Проверьте путь: {FILE_PATH}")
        return False
    
    try:
        # Путь в реестре
        key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
        
        # Открываем ключ реестра
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, 
                           winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE) as key:
            
            # Получаем текущее значение
            try:
                current_value, _ = winreg.QueryValueEx(key, "Userinit")
                print(f"\n📋 Текущее значение: {current_value}")
                
                # Проверяем, есть ли уже файл
                if FILE_PATH in current_value:
                    print("✅ Файл уже присутствует в Userinit")
                    return True
                
                # Добавляем файл
                new_value = f"{current_value}, {FILE_PATH}"
                winreg.SetValueEx(key, "Userinit", 0, winreg.REG_SZ, new_value)
                
                print(f"\n✅ Файл УСПЕШНО добавлен!")
                print(f"📋 Новое значение: {new_value}")
                
            except FileNotFoundError:
                # Создаем новый параметр
                winreg.SetValueEx(key, "Userinit", 0, winreg.REG_SZ, FILE_PATH)
                print(f"\n✅ Параметр Userinit создан!")
                print(f"📋 Значение: {FILE_PATH}")
        
        return True
        
    except PermissionError:
        print("\n❌ ОШИБКА: Нет прав администратора!")
        print("Запустите скрипт от имени администратора")
        return False
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    add_to_userinit_auto()
    input("\nНажмите Enter для выхода...")
