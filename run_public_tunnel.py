"""
Asisten Virtual Seasoldier — Public Tunnel Launcher
Menjalankan FastAPI Backend di laptop dan membuka Public HTTPS Tunnel (Cloudflare / Localtunnel)
sehingga frontend di Firebase Hosting (https://asisten-seasoldier.web.app/) atau GitHub Pages
dapat terhubung secara publik dari mana saja dengan aman dan instan.
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

def check_dependencies():
    """Memeriksa dependensi Python yang dibutuhkan."""
    missing = []
    for pkg in ["fastapi", "uvicorn", "groq", "dotenv"]:
        try:
            if pkg == "dotenv":
                import dotenv
            else:
                __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"[*] Menginstal dependensi yang belum ada: {', '.join(missing)}...", flush=True)
        backend_req = os.path.join(BASE_DIR, "backend", "requirements.txt")
        if os.path.exists(backend_req):
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", backend_req], check=False)
        else:
            subprocess.run([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn[standard]", "groq", "python-dotenv"], check=False)
        print("    [OK] Dependensi terinstal!", flush=True)

def check_or_download_cloudflared():
    """Memeriksa apakah cloudflared.exe tersedia, jika belum maka download otomatis."""
    if os.path.exists(CLOUDFLARED_EXE) and os.path.getsize(CLOUDFLARED_EXE) > 1000000:
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
    """Menampilkan log FastAPI ke konsol."""
    try:
        for line in iter(proc.stdout.readline, ''):
            if line:
                line_str = line.strip()
                if any(k in line_str for k in ["Uvicorn running", "Application startup complete", "ERROR", "Traceback", "WARNING"]):
                    print(f"      [FastAPI] {line_str}", flush=True)
    except Exception:
        pass

def start_tunnel(binary_path):
    """Menjalankan Cloudflare Tunnel dan mengambil Public HTTPS URL."""
    print("[3/3] Menghubungkan Cloudflare Tunnel...", flush=True)
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

    # Read output and find the public url
    for _ in range(60):
        line = proc.stdout.readline()
        if not line:
            if proc.poll() is not None:
                break
            time.sleep(0.2)
            continue
        
        match = url_pattern.search(line)
        if match:
            public_url = match.group(0)
            break
    
    return proc, public_url

def main():
    print("\n" + "="*68, flush=True)
    print("   🌊 ASISTEN VIRTUAL SEASOLDIER - PUBLIC TUNNEL LAUNCHER 🚀", flush=True)
    print("="*68 + "\n", flush=True)

    # 1. Cek dependensi Python
    check_dependencies()

    # 2. Siapkan Cloudflare Tunnel
    binary_path = check_or_download_cloudflared()

    # 3. Jalankan FastAPI
    fastapi_proc = start_fastapi()
    t_fastapi = threading.Thread(target=monitor_fastapi_logs, args=(fastapi_proc,), daemon=True)
    t_fastapi.start()

    # Tunggu backend siap sejenak
    time.sleep(1.5)

    # 4. Jalankan Tunnel
    if binary_path:
        tunnel_proc, public_url = start_tunnel(binary_path)
        if public_url:
            # Auto-publish backend URL to active_backend.json & deploy to Firebase CDN
            try:
                import json
                active_meta = {
                    "backend_url": public_url,
                    "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }
                active_file = os.path.join(BASE_DIR, "frontend", "active_backend.json")
                with open(active_file, "w", encoding="utf-8") as f:
                    json.dump(active_meta, f, indent=2)
                print(f"  ✅ active_backend.json diperbarui dengan URL: {public_url}", flush=True)
                
                # Auto-deploy ke Firebase Hosting di background thread
                def deploy_firebase():
                    try:
                        print("  🚀 Auto-deploying ke Firebase Hosting...", flush=True)
                        result = subprocess.run(
                            ["npx", "firebase", "deploy", "--only", "hosting", "--project", "asisten-seasoldier"],
                            cwd=BASE_DIR, shell=True,
                            capture_output=True, text=True, timeout=120
                        )
                        if result.returncode == 0:
                            print("  ✅ Firebase Hosting deploy berhasil! HP bisa langsung buka https://asisten-seasoldier.web.app/", flush=True)
                        else:
                            print(f"  ⚠️ Firebase deploy gagal (code {result.returncode}). Gunakan link ?backend= di bawah.", flush=True)
                    except Exception as ex:
                        print(f"  ⚠️ Firebase deploy error: {ex}", flush=True)
                
                deploy_thread = threading.Thread(target=deploy_firebase, daemon=True)
                deploy_thread.start()
            except Exception as e:
                print(f"[!] Gagal menulis active_backend.json: {e}", flush=True)

            auto_connect_link = f"https://asisten-seasoldier.web.app/?backend={public_url}"
            print("\n" + "="*70, flush=True)
            print("  🎉 SERVER & TUNNEL PUBLIK ASISTEN VIRTUAL BERHASIL AKTIF! 🎉", flush=True)
            print("="*70, flush=True)
            print(f"  📱 LINK AUTO-CONNECT (HP & LAPTOP):", flush=True)
            print(f"     👉 {auto_connect_link}", flush=True)
            print("  " + "-"*66, flush=True)
            print(f"  🌐 Public HTTPS Tunnel: {public_url}", flush=True)
            print(f"  💻 Local Endpoint     : http://localhost:{PORT}", flush=True)
            print(f"  🔥 Firebase Live Web  : https://asisten-seasoldier.web.app/ (Auto-Discovered)", flush=True)
            print("  " + "-"*66, flush=True)
            print("  ✨ CARA PENGGUNAAN DI HP & LAPTOP:", flush=True)
            print("  1. DI HP: Buka browser HP dan akses 'LINK AUTO-CONNECT' di atas.", flush=True)
            print("     (Sistem langsung otomatis tersambung 100% ONLINE!)", flush=True)
            print("  2. DI LAPTOP: Website akan terbuka otomatis atau klik link di atas.", flush=True)
            print("  3. Secara manual, Anda juga bisa memasukkan Public HTTPS URL", flush=True)
            print("     ke menu Pengaturan (ikon ⚙️) di pojok kanan atas website.", flush=True)
            print("="*70 + "\n", flush=True)
            print("  Tekan Ctrl + C di terminal ini untuk mematikan server & tunnel.\n", flush=True)

            # Auto-open browser on laptop
            try:
                import webbrowser
                webbrowser.open(auto_connect_link)
            except Exception:
                pass

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
            print("\n[!] Cloudflare Tunnel memerlukan beberapa detik tambahan untuk terhubung.", flush=True)
            print(f"    Server lokal Anda tetap aktif di http://localhost:{PORT}", flush=True)
    else:
        print(f"\n[*] Server lokal aktif di http://localhost:{PORT}", flush=True)

if __name__ == "__main__":
    main()
