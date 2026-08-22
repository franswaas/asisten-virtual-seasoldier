@echo off
title Deployment Asisten Virtual Seasoldier ke Firebase
cls

echo ====================================================================
echo   ASISTEN VIRTUAL SEASOLDIER - FIREBASE DEPLOYMENT LAUNCHER
echo ====================================================================
echo.

echo [1/3] Memeriksa instalasi Firebase CLI...
where firebase >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] Firebase CLI belum terinstal atau belum masuk PATH.
    echo     Silakan instal dengan perintah: npm install -g firebase-tools
    echo.
    pause
    exit /b 1
)

echo [OK] Firebase CLI terdeteksi!
echo.
echo ====================================================================
echo Pilihan Aksi:
echo [1] Pilih / Sambungkan Project Baru (firebase use --add)
echo [2] Deploy Frontend Saja (Firebase Hosting)
echo [3] Deploy Lengkap (Hosting + Cloud Functions Backend)
echo [4] Login Ulang Akun Firebase (firebase login)
echo [5] Keluar
echo ====================================================================
echo.

set /p opt="Pilih nomor (1/2/3/4/5): "

if "%opt%"=="1" (
    echo.
    echo [*] Mengambil daftar project Firebase dari akun Anda...
    firebase use --add
) else if "%opt%"=="2" (
    echo.
    echo [*] Memulai deploy Firebase Hosting...
    firebase deploy --only hosting
) else if "%opt%"=="3" (
    echo.
    echo [*] Memulai deploy Hosting dan Cloud Functions...
    firebase deploy
) else if "%opt%"=="4" (
    echo.
    echo [*] Membuka browser untuk login Firebase...
    firebase login
) else (
    echo [*] Keluar.
)

echo.
echo ====================================================================
echo Selesai! Tekan tombol apapun untuk menutup jendela ini.
echo ====================================================================
pause > nul
