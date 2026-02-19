import winreg
import os
import sys
from pathlib import Path

# ===== УКАЖИТЕ ПУТЬ К ВАШЕМУ ФАЙЛУ ЗДЕСЬ =====
FILE_PATH = r"C:\Users\1\Desktop\RFHRSF\start.bat"  # ИЗМЕНИТЕ ЭТОТ ПУТЬ!
# ==============================================

def add_to_userinit():
    """
    Добавляет файл в Userinit
    """
    try:
        key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
        
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, 
                           winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE) as key:
            
            try:
                current_value, _ = winreg.QueryValueEx(key, "Userinit")
                print(f"📋 Текущее Userinit: {current_value}")
                
                if FILE_PATH not in current_value:
                    new_value = f"{current_value}, {FILE_PATH}"
                    winreg.SetValueEx(key, "Userinit", 0, winreg.REG_SZ, new_value)
                    print(f"✅ Добавлено в Userinit")
                else:
                    print(f"⚠️ Файл уже есть в Userinit")
                    
            except FileNotFoundError:
                winreg.SetValueEx(key, "Userinit", 0, winreg.REG_SZ, FILE_PATH)
                print(f"✅ Создан Userinit с файлом")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка Userinit: {e}")
        return False

def add_to_shell():
    """
    Добавляет файл в Shell (альтернативная оболочка)
    """
    try:
        key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
        
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0,
                           winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE) as key:
            
            try:
                current_shell, _ = winreg.QueryValueEx(key, "Shell")
                print(f"📋 Текущая Shell: {current_shell}")
                
                # Проверяем, не запускаем ли мы explorer.exe
                if "explorer.exe" in current_shell.lower():
                    # Если запускаем explorer.exe, добавляем наш файл после него
                    new_shell = f"explorer.exe, {FILE_PATH}"
                else:
                    # Иначе добавляем в начало или конец?
                    if FILE_PATH not in current_shell:
                        new_shell = f"{FILE_PATH}, {current_shell}"
                    else:
                        print(f"⚠️ Файл уже есть в Shell")
                        return True
                
                winreg.SetValueEx(key, "Shell", 0, winreg.REG_SZ, new_shell)
                print(f"✅ Добавлено в Shell")
                
            except FileNotFoundError:
                # Если Shell нет, создаем с explorer.exe и нашим файлом
                new_shell = f"explorer.exe, {FILE_PATH}"
                winreg.SetValueEx(key, "Shell", 0, winreg.REG_SZ, new_shell)
                print(f"✅ Создана Shell с файлом")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка Shell: {e}")
        return False

def add_to_shell_registry_current_user():
    """
    Добавляет в Shell для текущего пользователя (HKEY_CURRENT_USER)
    """
    try:
        key_path = r"Software\Microsoft\Windows NT\CurrentVersion\Winlogon"
        
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0,
                           winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE) as key:
            
            try:
                current_shell, _ = winreg.QueryValueEx(key, "Shell")
                print(f"📋 Текущая Shell (HKCU): {current_shell}")
                
                if FILE_PATH not in current_shell:
                    new_shell = f"{current_shell}, {FILE_PATH}"
                    winreg.SetValueEx(key, "Shell", 0, winreg.REG_SZ, new_shell)
                    print(f"✅ Добавлено в Shell (HKCU)")
                else:
                    print(f"⚠️ Файл уже есть в Shell (HKCU)")
                    
            except FileNotFoundError:
                winreg.SetValueEx(key, "Shell", 0, winreg.REG_SZ, f"explorer.exe, {FILE_PATH}")
                print(f"✅ Создана Shell (HKCU) с файлом")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка Shell (HKCU): {e}")
        return False

def add_to_safe_boot_alternative_shell():
    """
    Добавляет в альтернативную оболочку для безопасного режима
    """
    try:
        key_path = r"SYSTEM\CurrentControlSet\Control\SafeBoot"
        
        # Пробуем добавить в различные подразделы SafeBoot
        subkeys = [r"Minimal\AlternateShell", r"Network\AlternateShell"]
        
        for subkey in subkeys:
            try:
                full_path = f"{key_path}\\{subkey}"
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, full_path, 0,
                                   winreg.KEY_SET_VALUE) as key:
                    
                    winreg.SetValueEx(key, "", 0, winreg.REG_SZ, FILE_PATH)
                    print(f"✅ Добавлено в {subkey}")
                    
            except FileNotFoundError:
                print(f"⚠️ Ключ {subkey} не найден")
            except Exception as e:
                print(f"❌ Ошибка в {subkey}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка SafeBoot: {e}")
        return False

def add_to_all_shell_entries():
    """
    Добавляет файл во все возможные Shell-записи
    """
    print("=" * 60)
    print("ДОБАВЛЕНИЕ ФАЙЛА В SHELL/USERINIT РЕЕСТРА")
    print("=" * 60)
    print(f"Файл: {FILE_PATH}")
    
    # Проверяем существование файла
    if not os.path.exists(FILE_PATH):
        print(f"\n❌ ОШИБКА: Файл не найден!")
        print(f"Проверьте путь: {FILE_PATH}")
        
        # Предлагаем создать файл
        create = input("\nСоздать файл? (y/n): ").lower()
        if create == 'y':
            create_file(FILE_PATH, "@echo off\necho Запущен из реестра\ntimeout /t 10")
        else:
            return False
    
    # Проверяем права администратора
    try:
        test_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                  r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", 
                                  0, winreg.KEY_READ)
        winreg.CloseKey(test_key)
    except PermissionError:
        print("\n❌ Нет прав администратора! Запустите скрипт от имени администратора.")
        return False
    
    print("\n🔄 Добавление в реестр...\n")
    
    # Добавляем во все места
    success = []
    
    if add_to_userinit():
        success.append("Userinit")
    
    if add_to_shell():
        success.append("Shell (HKLM)")
    
    if add_to_shell_registry_current_user():
        success.append("Shell (HKCU)")
    
    # Опционально - добавить в безопасный режим
    add_safe = input("\nДобавить в безопасный режим? (y/n): ").lower()
    if add_safe == 'y':
        if add_to_safe_boot_alternative_shell():
            success.append("SafeBoot")
    
    # Результат
    print("\n" + "=" * 60)
    if success:
        print(f"✅ УСПЕШНО ДОБАВЛЕНО В: {', '.join(success)}")
        print("\n📌 Изменения вступят после перезагрузки!")
        print("⚠️ ВНИМАНИЕ: Будьте осторожны с изменениями Shell!")
        print("   Неправильные изменения могут помешать загрузке Windows.")
    else:
        print("❌ НЕ УДАЛОСЬ ДОБАВИТЬ ФАЙЛ")
    
    return bool(success)

def create_file(file_path, content=""):
    """
    Создает файл по указанному пути
    """
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n✅ Файл создан: {path.absolute()}")
        print(f"📁 Папка: {path.parent}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при создании файла: {e}")
        return False

if __name__ == "__main__":
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'create':
        # Режим создания файла
        content = """@echo off
echo Программа запущена из реестра
echo Путь: %~f0
echo Дата: %date% %time%
pause
"""
        create_file(FILE_PATH, content)
    else:
        # Основной режим - добавление в реестр
        add_to_all_shell_entries()
    
    print("\n" + "=" * 60)
    input("Нажмите Enter для выхода...")
