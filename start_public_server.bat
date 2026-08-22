@echo off
title Asisten Virtual Seasoldier - Public Server & Tunnel
cls

echo ===================================================================
echo   ASISTEN VIRTUAL SEASOLDIER - PUBLIC SERVER & TUNNEL LAUNCHER
echo ===================================================================
echo.

set "PY_EXE="

:: 1. Cek python di PATH
where python >nul 2>nul
if %errorlevel% equ 0 (
    set "PY_EXE=python"
    goto :found_python
)

:: 2. Cek py launcher
where py >nul 2>nul
if %errorlevel% equ 0 (
    set "PY_EXE=py"
    goto :found_python
)

:: 3. Cek AppData Local Programs
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%D\python.exe" (
        set "PY_EXE=%%D\python.exe"
        goto :found_python
    )
)

:: 4. Cek Program Files
for /d %%D in ("C:\Program Files\Python*") do (
    if exist "%%D\python.exe" (
        set "PY_EXE=%%D\python.exe"
        goto :found_python
    )
)

echo [!] Python tidak ditemukan di sistem Anda.
echo     Silakan instal Python dari https://www.python.org/downloads/
echo     (Pastikan centang "Add Python to PATH" saat instalasi).
echo.
pause
exit /b 1

:found_python
echo [OK] Menggunakan Python: %PY_EXE%
echo [*] Memulai server backend dan Cloudflare Tunnel...
echo.
"%PY_EXE%" "%~dp0run_public_tunnel.py"

echo.
echo ===================================================================
echo Server berhenti. Tekan tombol apapun untuk keluar.
echo ===================================================================
pause > nul
