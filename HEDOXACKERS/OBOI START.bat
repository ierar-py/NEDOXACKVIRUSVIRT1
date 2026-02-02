@echo off 
REG ADD "HKEY_CURRENT_USER\Control Panel\Desktop" /v Wallpaper /t REG_SZ /d "C:\Users\MSI\Desktop\HEDOXACKERS\images (6).jpeg" /f 
RUNDLL32.EXE user32.dll,UpdatePerUserSystemParameters
