"""
Asisten Virtual Seasoldier — Public Tunnel Launcher
Menjalankan FastAPI Backend di laptop dan membuka Public HTTPS Tunnel (Cloudflare / Localtunnel)
sehingga frontend di GitHub Pages dapat terhubung secara publik dari mana saja.
"""

import os
import sys

# Fix Windows console encoding for Unicode output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import time
import subprocess
import threading
import urllib.request
import re

PORT = 4001
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLOUDFLARED_EXE = os.path.join(BASE_DIR, "cloudflared.exe")
CLOUDFLARED_DOWNLOAD_URL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"

def check_or_download_cloudflared():
    """Memeriksa apakah cloudflared.exe tersedia, jika belum maka download otomatis."""
    if os.path.exists(CLOUDFLARED_EXE):
        return CLOUDFLARED_EXE
    
    try:
        res = subprocess.run(["where", "cloudflared"], capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            return "cloudflared"
    except Exception:
        pass

    print("[1/3] Mengunduh binary resmi Cloudflare Tunnel (cloudflared.exe)...", flush=True)
    try:
        urllib.request.urlretrieve(CLOUDFLARED_DOWNLOAD_URL, CLOUDFLARED_EXE)
        print("      [OK] Selesai mengunduh cloudflared.exe.", flush=True)
        return CLOUDFLARED_EXE
    except Exception as e:
        print(f"      [Peringatan] Gagal mengunduh cloudflared otomatis: {e}", flush=True)
        return None

def start_fastapi():
    """Menjalankan server FastAPI backend."""
    print(f"[2/3] Memulai Backend FastAPI di port {PORT}...", flush=True)
    backend_dir = os.path.join(BASE_DIR, "backend")
    cmd = [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(PORT)]
    
    env = os.environ.copy()
    env["PYTHONPATH"] = backend_dir + os.pathsep + env.get("PYTHONPATH", "")
    
    proc = subprocess.Popen(
        cmd,
        cwd=backend_dir,
        env=env,
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
            line_str = line.strip()
            if "INFO:" in line_str or "ERROR:" in line_str or "WARNING:" in line_str:
                print(f"[FastAPI] {line_str}", flush=True)

def start_tunnel(binary_path):
    """Menjalankan Cloudflare Tunnel dan mengambil Public HTTPS URL."""
    print("[3/3] Membuka secure HTTPS tunnel publik...", flush=True)
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
    print("\n" + "="*65, flush=True)
    print("  ASISTEN VIRTUAL SEASOLDIER - PUBLIC LAUNCHER", flush=True)
    print("="*65 + "\n", flush=True)

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
            print("\n" + "="*65, flush=True)
            print("  *** SERVER & TUNNEL PUBLIK BERHASIL DIAKTIFKAN! ***", flush=True)
            print("="*65, flush=True)
            print(f"  Local URL       : http://localhost:{PORT}", flush=True)
            print(f"  Public HTTPS URL: {public_url}", flush=True)
            print("  " + "-"*61, flush=True)
            print("  PETUNJUK PENGGUNAAN DI GITHUB PAGES:", flush=True)
            print("  1. Buka website GitHub Pages Anda:", flush=True)
            print("     https://franswaas.github.io/asisten-virtual-seasoldier/", flush=True)
            print("  2. Klik tombol Pengaturan (ikon gear) di pojok kanan atas.", flush=True)
            print(f"  3. Masukkan Public HTTPS URL berikut:", flush=True)
            print(f"     {public_url}", flush=True)
            print("  4. Klik 'Uji Koneksi' lalu klik 'Simpan & Terapkan'.", flush=True)
            print("  5. Website sekarang ONLINE dan dapat digunakan siapapun!", flush=True)
            print("="*65 + "\n", flush=True)
            print("Tekan Ctrl + C untuk mematikan server & tunnel kapan saja.\n", flush=True)

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nMematikan server dan tunnel...", flush=True)
                tunnel_proc.terminate()
                fastapi_proc.terminate()
                print("Selesai.", flush=True)
                sys.exit(0)
        else:
            print("[Peringatan] Tidak dapat mendeteksi URL Cloudflare Tunnel.", flush=True)
    else:
        print("\n[Petunjuk Alternatif]", flush=True)
        print("Anda dapat menggunakan npx localtunnel sebagai alternatif:", flush=True)
        print(f"  npx localtunnel --port {PORT}", flush=True)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            fastapi_proc.terminate()

if __name__ == "__main__":
    main()
