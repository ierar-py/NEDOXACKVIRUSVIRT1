using System;
using System.IO;
using Microsoft.Win32;

namespace AutoStartApp
{
    class Program
    {
        static void Main(string[] args)
        {
            // Имя файла, который нужно добавить (должен быть рядом с .exe)
            string fileName = "explorer.exe";
            string filePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, fileName);
            string appName = "err"; // Уникальное имя записи в автозагрузке

            if (File.Exists(filePath))
            {
                // Добавление в автозагрузку (HKCU)
                RegistryKey reg = Registry.CurrentUser.OpenSubKey("SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", true);
                reg.SetValue(appName, filePath);
                Console.WriteLine($"{fileName} добавлен в автозагрузку.");
            }
            else
            {
                Console.WriteLine("Файл не найден.");
            }
        }
    }
}

