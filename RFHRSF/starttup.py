import os
import shutil
import winreg
import getpass
from pathlib import Path

class AutoRunManager:
    def __init__(self):
        self.username = getpass.getuser()
        
    def add_to_startup_folder(self, source_path):
        """Добавление в папку автозагрузки текущего пользователя"""
        try:
            # Путь к папке автозагрузки
            startup_folder = os.path.join(
                os.environ['APPDATA'],
                'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
            )
            
            # Получаем имя файла
            filename = os.path.basename(source_path)
            destination = os.path.join(startup_folder, filename)
            
            # Копируем файл
            shutil.copy2(source_path, destination)
            print(f"[+] Файл добавлен в папку автозагрузки пользователя: {destination}")
            return True
        except Exception as e:
            print(f"[-] Ошибка при добавлении в папку автозагрузки: {e}")
            return False
    
    def add_to_all_users_startup(self, source_path):
        """Добавление в папку автозагрузки для всех пользователей (требуются права администратора)"""
        try:
            startup_folder_all = os.path.join(
                'C:\\ProgramData',
                'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
            )
            
            filename = os.path.basename(source_path)
            destination = os.path.join(startup_folder_all, filename)
            
            shutil.copy2(source_path, destination)
            print(f"[+] Файл добавлен в общую папку автозагрузки: {destination}")
            return True
        except Exception as e:
            print(f"[-] Ошибка при добавлении в общую папку автозагрузки: {e}")
            return False
    
    def add_to_registry_current_user(self, file_path, name="MyApp"):
        """Добавление в реестр HKEY_CURRENT_USER (для текущего пользователя)"""
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            # Открываем ключ реестра
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                key_path,
                0,
                winreg.KEY_SET_VALUE
            )
            
            # Устанавливаем значение
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, file_path)
            winreg.CloseKey(key)
            
            print(f"[+] Файл добавлен в реестр (HKCU): {name} -> {file_path}")
            return True
        except Exception as e:
            print(f"[-] Ошибка при добавлении в реестр HKCU: {e}")
            return False
    
    def add_to_registry_local_machine(self, file_path, name="MyApp"):
        """Добавление в реестр HKEY_LOCAL_MACHINE (для всех пользователей, требуются права администратора)"""
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            # Открываем ключ реестра
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                key_path,
                0,
                winreg.KEY_SET_VALUE
            )
            
            # Устанавливаем значение
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, file_path)
            winreg.CloseKey(key)
            
            print(f"[+] Файл добавлен в реестр (HKLM): {name} -> {file_path}")
            return True
        except Exception as e:
            print(f"[-] Ошибка при добавлении в реестр HKLM: {e}")
            return False
    
    def add_to_registry_run_once(self, file_path, name="MyAppOnce"):
        """Добавление в RunOnce (выполнится один раз при следующем запуске)"""
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\RunOnce"
            
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                key_path,
                0,
                winreg.KEY_SET_VALUE
            )
            
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, file_path)
            winreg.CloseKey(key)
            
            print(f"[+] Файл добавлен в RunOnce: {name} -> {file_path}")
            return True
        except Exception as e:
            print(f"[-] Ошибка при добавлении в RunOnce: {e}")
            return False
    
    def create_task_scheduler(self, file_path, task_name="MyTask"):
        """Создание задачи в планировщике (требуются права администратора)"""
        try:
            # Создаем XML для задачи
            import xml.etree.ElementTree as ET
            from datetime import datetime, timedelta
            
            # Команда для создания задачи через schtasks
            command = f'schtasks /create /tn "{task_name}" /tr "{file_path}" /sc onlogon /ru "{self.username}" /f'
            
            # Выполняем команду
            result = os.system(command)
            
            if result == 0:
                print(f"[+] Задача создана в планировщике: {task_name}")
                return True
            else:
                print(f"[-] Ошибка при создании задачи в планировщике")
                return False
        except Exception as e:
            print(f"[-] Ошибка: {e}")
            return False
    
    def add_to_windows_services(self, file_path, service_name="MyService"):
        """Добавление как служба Windows (требуются права администратора)"""
        try:
            # Создание службы через sc
            command = f'sc create "{service_name}" binPath= "{file_path}" start= auto'
            result = os.system(command)
            
            if result == 0:
                print(f"[+] Служба создана: {service_name}")
                return True
            else:
                print(f"[-] Ошибка при создании службы")
                return False
        except Exception as e:
            print(f"[-] Ошибка: {e}")
            return False
    
    def add_to_policies_run(self, file_path, name="MyPolicy"):
        """Добавление в политики (требуются права администратора)"""
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run"
            
            # Создаем ключ если не существует
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            
            # Устанавливаем значение
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, file_path)
            winreg.CloseKey(key)
            
            print(f"[+] Файл добавлен в политики: {name}")
            return True
        except Exception as e:
            print(f"[-] Ошибка при добавлении в политики: {e}")
            return False

def main():
    # Создаем экземпляр менеджера
    manager = AutoRunManager()
    
    # УКАЖИТЕ ЗДЕСЬ ПУТЬ К ВАШЕМУ ФАЙЛУ
    file_to_add = r"C:\Users\1\Desktop\RFHRSF\start.bat"
    
    # Имя для записи в реестре/задачах
    entry_name = "MyApplication"
    
    print("=" * 50)
    print("ДОБАВЛЕНИЕ В АВТОЗАГРУЗКУ WINDOWS")
    print("=" * 50)
    print(f"Файл: {file_to_add}")
    print(f"Имя записи: {entry_name}")
    print("-" * 50)
    
    # Проверяем существование файла
    if not os.path.exists(file_to_add):
        print(f"[-] Файл не найден: {file_to_add}")
        return
    
    print("\n[+] Начинаем добавление в автозагрузку...\n")
    
    # Добавляем во все места автозагрузки
    manager.add_to_startup_folder(file_to_add)
    manager.add_to_all_users_startup(file_to_add)
    manager.add_to_registry_current_user(file_to_add, entry_name)
    manager.add_to_registry_local_machine(file_to_add, f"{entry_name}_Machine")
    manager.add_to_registry_run_once(file_to_add, f"{entry_name}_Once")
    manager.create_task_scheduler(file_to_add, f"{entry_name}_Task")
    manager.add_to_windows_services(file_to_add, f"{entry_name}_Service")
    manager.add_to_policies_run(file_to_add, f"{entry_name}_Policy")
    
    print("\n" + "=" * 50)
    print("ГОТОВО!")
    print("=" * 50)
    print("\nПримечания:")
    print("- Некоторые методы требуют прав администратора")
    print("- Для служб нужен исполняемый файл, поддерживающий работу как служба")
    print("- Проверьте результаты выполнения каждой операции выше")

if __name__ == "__main__":
    # Проверяем, запущен ли скрипт с правами администратора
    import ctypes
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    if is_admin():
        print("[+] Запущено с правами администратора")
    else:
        print("[-] Запущено без прав администратора")
        print("    Некоторые функции могут не работать\n")
    
    main()
