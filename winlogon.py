import os
import sys
import winreg
import argparse

def add_to_winlogon(file_path, section="Shell", create_backup=True):
    """
    Добавляет программу в Winlogon через реестр
    Путь: HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon
    
    Args:
        file_path (str): Полный путь к исполняемому файлу
        section (str): Секция Winlogon ("Shell", "Userinit", "Notify")
        create_backup (bool): Создать резервную копию текущих значений
    
    Returns:
        bool: True если успешно, False в случае ошибки
    """
    try:
        # Проверяем существование файла
        if not os.path.exists(file_path):
            print(f"Ошибка: Файл '{file_path}' не найден")
            return False
        
        # Преобразуем в абсолютный путь
        file_path = os.path.abspath(file_path)
        
        # Проверяем расширение файла
        if not file_path.lower().endswith(('.exe', '.bat', '.cmd', '.com')):
            print(f"Предупреждение: Файл '{file_path}' может не быть исполняемым")
        
        # Открываем ключ Winlogon
        key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
        
        # Для 64-битных систем, если запущен 32-битный Python
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                key_path,
                0,
                winreg.KEY_READ | winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY
            )
        except FileNotFoundError:
            # Пробуем без флага WOW64
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                key_path,
                0,
                winreg.KEY_READ | winreg.KEY_WRITE
            )
        
        # Читаем текущее значение
        try:
            current_value, value_type = winreg.QueryValueEx(key, section)
            
            if create_backup:
                print(f"Текущее значение {section}:")
                print(f"  {current_value}")
                
                # Создаем резервную копию в отдельном ключе
                backup_key = winreg.CreateKey(key, f"{section}_Backup")
                winreg.SetValueEx(backup_key, "Original", 0, winreg.REG_SZ, current_value)
                winreg.CloseKey(backup_key)
                print(f"✓ Резервная копия создана в {section}_Backup")
        except FileNotFoundError:
            current_value = ""
            value_type = winreg.REG_SZ
        
        # Формируем новое значение в зависимости от секции
        if section.lower() == "shell":
            # Shell обычно содержит explorer.exe, можно добавить через запятую
            if current_value:
                if file_path.lower() not in current_value.lower():
                    new_value = f"{current_value}, {file_path}"
                else:
                    print(f"Файл уже присутствует в {section}")
                    winreg.CloseKey(key)
                    return True
            else:
                new_value = f"explorer.exe, {file_path}"
                
        elif section.lower() == "userinit":
            # Userinit обычно содержит userinit.exe,
            if current_value:
                if file_path.lower() not in current_value.lower():
                    new_value = f"{current_value}, {file_path}"
                else:
                    print(f"Файл уже присутствует в {section}")
                    winreg.CloseKey(key)
                    return True
            else:
                new_value = f"C:\\Windows\\system32\\userinit.exe, {file_path}"
                
        elif section.lower() == "notify":
            # Notify - это отдельные ключи, а не список
            print("Секция Notify требует создания отдельного подключа")
            notify_key = winreg.CreateKey(key, "Notify")
            app_key = winreg.CreateKey(notify_key, os.path.splitext(os.path.basename(file_path))[0])
            
            winreg.SetValueEx(app_key, "DllName", 0, winreg.REG_SZ, file_path)
            winreg.SetValueEx(app_key, "Startup", 0, winreg.REG_SZ, "Boot")
            winreg.SetValueEx(app_key, "Asynchronous", 0, winreg.REG_DWORD, 1)
            
            winreg.CloseKey(app_key)
            winreg.CloseKey(notify_key)
            
            print(f"✓ Программа добавлена в Winlogon\\Notify")
            winreg.CloseKey(key)
            return True
        else:
            new_value = file_path
        
        # Устанавливаем новое значение
        winreg.SetValueEx(key, section, 0, winreg.REG_SZ, new_value)
        winreg.CloseKey(key)
        
        print(f"✓ Программа успешно добавлена в Winlogon")
        print(f"  Секция: {section}")
        print(f"  Новое значение: {new_value}")
        print(f"  Расположение: HKLM\\{key_path}")
        
        # Предупреждение
        print("\n⚠ ВНИМАНИЕ: Изменение Winlogon может повлиять на загрузку системы!")
        print("  Для восстановления используйте функцию restore_winlogon_backup()")
        
        return True
        
    except PermissionError:
        print("Ошибка: Недостаточно прав для записи в реестр")
        print("Обязательно запустите скрипт от имени администратора!")
        return False
    except Exception as e:
        print(f"Ошибка при добавлении в Winlogon: {e}")
        return False

def restore_winlogon_backup(section="Shell"):
    """
    Восстанавливает исходное значение Winlogon из резервной копии
    
    Args:
        section (str): Секция Winlogon для восстановления
    """
    try:
        key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
        
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            key_path,
            0,
            winreg.KEY_READ | winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY
        )
        
        # Читаем резервную копию
        try:
            backup_key = winreg.OpenKey(key, f"{section}_Backup")
            original_value, _ = winreg.QueryValueEx(backup_key, "Original")
            winreg.CloseKey(backup_key)
            
            # Восстанавливаем
            winreg.SetValueEx(key, section, 0, winreg.REG_SZ, original_value)
            
            # Удаляем резервную копию
            winreg.DeleteKey(key, f"{section}_Backup")
            
            print(f"✓ Значение {section} восстановлено: {original_value}")
            
        except FileNotFoundError:
            print(f"Резервная копия для {section} не найдена")
            
        winreg.CloseKey(key)
        return True
        
    except PermissionError:
        print("Ошибка: Требуются права администратора")
        return False
    except Exception as e:
        print(f"Ошибка при восстановлении: {e}")
        return False

def show_winlogon_values():
    """
    Показывает текущие значения Winlogon
    """
    try:
        key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
        
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            key_path,
            0,
            winreg.KEY_READ | winreg.KEY_WOW64_64KEY
        )
        
        print("\n=== Текущие значения Winlogon ===\n")
        
        # Основные секции
        sections = ["Shell", "Userinit", "Notify", "System", "VMApplet"]
        
        for section in sections:
            try:
                value, _ = winreg.QueryValueEx(key, section)
                print(f"{section}:")
                print(f"  {value}\n")
            except FileNotFoundError:
                print(f"{section}: (не найден)\n")
        
        # Показываем подключи Notify если есть
        try:
            notify_key = winreg.OpenKey(key, "Notify")
            print("Notify subkeys:")
            
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(notify_key, i)
                    subkey = winreg.OpenKey(notify_key, subkey_name)
                    dll_name, _ = winreg.QueryValueEx(subkey, "DllName")
                    print(f"  [{i+1}] {subkey_name}: {dll_name}")
                    winreg.CloseKey(subkey)
                    i += 1
                except OSError:
                    break
            
            winreg.CloseKey(notify_key)
            print()
        except FileNotFoundError:
            pass
        
        winreg.CloseKey(key)
        return True
        
    except PermissionError:
        print("Ошибка: Недостаточно прав для чтения реестра")
        return False
    except Exception as e:
        print(f"Ошибка при чтении Winlogon: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Управление Winlogon в Windows')
    parser.add_argument('file', nargs='?', help='Путь к файлу для добавления в Winlogon')
    parser.add_argument('--section', '-s', default='Shell', 
                       choices=['Shell', 'Userinit', 'Notify'],
                       help='Секция Winlogon (по умолчанию: Shell)')
    parser.add_argument('--restore', '-r', metavar='SECTION', 
                       help='Восстановить секцию из резервной копии')
    parser.add_argument('--show', action='store_true', 
                       help='Показать текущие значения Winlogon')
    parser.add_argument('--no-backup', action='store_true',
                       help='Не создавать резервную копию')
    
    args = parser.parse_args()
    
    # Проверяем права администратора
    import ctypes
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("⚠ ВНИМАНИЕ: Этот скрипт требует прав администратора!")
        print("  Перезапустите его от имени администратора.\n")
        
        # Пробуем перезапустить с правами администратора
        if args.file or args.restore or args.show:
            response = input("Перезапустить с правами администратора? (y/n): ")
            if response.lower() == 'y':
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, " ".join(sys.argv), None, 1
                )
                return
    
    if args.show:
        show_winlogon_values()
    elif args.restore:
        restore_winlogon_backup(args.restore)
    elif args.file:
        add_to_winlogon(args.file, args.section, not args.no_backup)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
