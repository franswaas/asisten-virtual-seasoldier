"""
Asisten Virtual Seasoldier — Public Tunnel Launcher
Menjalankan FastAPI Backend di laptop dan membuka Public HTTPS Tunnel (Cloudflare / Localtunnel)
sehingga frontend di GitHub Pages dapat terhubung secara publik dari mana saja.
"""

import os
import sys
import time
import subprocess
import threading
import urllib.request
import re

PORT = 4001
CLOUDFLARED_EXE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cloudflared.exe")
CLOUDFLARED_DOWNLOAD_URL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"

def check_or_download_cloudflared():
    """Memeriksa apakah cloudflared.exe tersedia, jika belum maka download otomatis."""
    if os.path.exists(CLOUDFLARED_EXE):
        return CLOUDFLARED_EXE
    
    # Cek apakah cloudflared ada di PATH sistem
    try:
        res = subprocess.run(["where", "cloudflared"], capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            return "cloudflared"
    except Exception:
        pass

    print("[1/3] Mengunduh binary resmi Cloudflare Tunnel (cloudflared.exe)...")
    try:
        urllib.request.urlretrieve(CLOUDFLARED_DOWNLOAD_URL, CLOUDFLARED_EXE)
        print("      ✓ Selesai mengunduh cloudflared.exe.")
        return CLOUDFLARED_EXE
    except Exception as e:
        print(f"      [Peringatan] Gagal mengunduh cloudflared otomatis: {e}")
        return None

def start_fastapi():
    """Menjalankan server FastAPI backend."""
    print(f"[2/3] Memulai Backend FastAPI di port {PORT}...")
    cwd = os.path.dirname(os.path.abspath(__file__))
    cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", str(PORT)]
    
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding="utf-8",
        errors="replace"
    )
    return proc

def monitor_fastapi_logs(proc):
    """Menampilkan log FastAPI."""
    for line in iter(proc.stdout.readline, ''):
        if line:
            # Saring log agar terminal tetap bersih
            if "INFO:" in line or "ERROR:" in line or "WARNING:" in line:
                print(f"[FastAPI] {line.strip()}")

def start_tunnel(binary_path):
    """Menjalankan Cloudflare Tunnel dan mengambil Public HTTPS URL."""
    print("[3/3] Membuka secure HTTPS tunnel publik...")
    cmd = [binary_path, "tunnel", "--url", f"http://127.0.0.1:{PORT}"]
    
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding="utf-8",
        errors="replace"
    )
    
    public_url = None
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

    for line in iter(proc.stdout.readline, ''):
        if line:
            match = url_pattern.search(line)
            if match:
                public_url = match.group(0)
                break
    
    return proc, public_url

def main():
    print("\n" + "="*65)
    print("  ASISTEN VIRTUAL SEASOLDIER — PUBLIC LAUNCHER (GITHUB PAGES + LAPTOP)")
    print("="*65 + "\n")

    # 1. Siapkan Cloudflare Tunnel
    binary_path = check_or_download_cloudflared()

    # 2. Jalankan FastAPI
    fastapi_proc = start_fastapi()
    t_fastapi = threading.Thread(target=monitor_fastapi_logs, args=(fastapi_proc,), daemon=True)
    t_fastapi.start()

    # Tunggu backend siap
    time.sleep(2)

    # 3. Jalankan Tunnel
    if binary_path:
        tunnel_proc, public_url = start_tunnel(binary_path)
        if public_url:
            print("\n" + "="*65)
            print("  🎉 SERVER & TUNNEL PUBLIK BERHASIL DIAKTIFKAN!")
            print("="*65)
            print(f"  📍 Local URL       : http://localhost:{PORT}")
            print(f"  🌐 Public HTTPS URL: {public_url}")
            print("  " + "-"*61)
            print("  PETUNJUK PENGGUNAAN DI GITHUB PAGES:")
            print("  1. Buka link web GitHub Pages Anda.")
            print("  2. Klik tombol '⚙️' (Pengaturan Server) di pojok kanan atas.")
            print(f"  3. Masukkan Public HTTPS URL di atas:")
            print(f"     👉 {public_url}")
            print("  4. Klik 'Simpan & Terapkan'.")
            print("  5. Sistem siap diakses oleh publik di seluruh dunia!")
            print("="*65 + "\n")
            print("Tekan Ctrl + C untuk mematikan server & tunnel kapan saja.\n")

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nMematikan server dan tunnel...")
                tunnel_proc.terminate()
                fastapi_proc.terminate()
                print("Selesai.")
                sys.exit(0)
        else:
            print("[Peringatan] Tidak dapat mendeteksi URL Cloudflare Tunnel.")
    else:
        print("\n[Petunjuk Alternatif]")
        print("Anda dapat menggunakan npx localtunnel sebagai alternatif:")
        print(f"  npx localtunnel --port {PORT}")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            fastapi_proc.terminate()

if __name__ == "__main__":
    main()
