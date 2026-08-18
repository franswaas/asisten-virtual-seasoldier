# Panduan Setup & Akses Asisten Virtual Seasoldier

Dokumen ini menjelaskan langkah-langkah menjalankan backend di laptop Anda secara lokal, melakukan hosting frontend di **GitHub Pages**, dan menghubungkan keduanya sehingga web dapat diakses oleh publik secara sementara.

---

## Arsitektur & Cara Kerja

```
[Pengunjung / Web Browser]
       │
       ▼
[Frontend: GitHub Pages (https://<username>.github.io/<repo>/)]
       │
       ▼ (Permintaan REST / Streaming SSE)
[Tunnel Publik: Cloudflare Tunnel / LocalTunnel / Ngrok]
       │
       ▼
[Backend di Laptop: FastAPI Port 4001]
       │
       ├──► [Groq AI LLM (Llama 3.3 70B)]
       └──► [Knowledge Base Seasoldier (BM25/TF-IDF RAG)]
```

---

## 1. Menjalankan Backend di Laptop

### A. Prasyarat
- **Python 3.10+** terpasang di laptop.
- Koneksi internet (untuk akses API Groq).

### B. Langkah Instalasi Dependensi
Buka Terminal / PowerShell di folder proyek:

```powershell
cd "e:\AI Agent\Asisten Virtual Seasoldier\backend"

# Buat virtual environment (opsional namun disarankan)
python -m venv venv
.\venv\Scripts\activate

# Install dependensi
pip install -r requirements.txt
```

### C. Menjalankan Server Backend
```powershell
# Jalankan server
python main.py
```
Server akan aktif di: **`http://localhost:4001`**
Anda dapat menguji di browser dengan membuka: `http://localhost:4001` (akan langsung membuka frontend antarmuka).

---

## 2. Menjalankan Backend & Tunnel Otomatis (1-Click)

Kami telah menyediakan skrip otomatis yang menjalankan FastAPI sekaligus membuat **Cloudflare Tunnel (HTTPS)** secara instan:

### Cara 1: Menggunakan Script Python (Otomatis & Mudah)
Cukup jalankan perintah berikut di root folder proyek:
```powershell
python run_public_tunnel.py
```
*Skrip ini akan otomatis mengunduh binary resmi Cloudflare jika belum ada, memulai FastAPI, dan langsung menampilkan URL HTTPS publik di terminal.*

### Cara 2: Double Click File Batch di Windows
Anda juga dapat langsung membuka Windows Explorer dan melakukan **Double Click** pada file:
👉 **`start_public_server.bat`**

---

## 3. Cara Deploy Frontend ke GitHub Pages

1. **Buat Repository di GitHub**:
   - Buka [github.com/new](https://github.com/new).
   - Buat repository baru, misalnya: `asisten-virtual-seasoldier`.
   - Pilih opsi **Public**.

2. **Push Kode ke GitHub**:
   Jalankan perintah berikut di terminal:
   ```bash
   git init
   git add .
   git commit -m "feat: initial commit Asisten Virtual Seasoldier"
   git branch -M main
   git remote add origin https://github.com/<username-anda>/<nama-repo>.git
   git push -u origin main
   ```

3. **Aktifkan GitHub Pages**:
   - Masuk ke tab **Settings** -> **Pages** pada repository GitHub Anda.
   - Pada bagian **Build and deployment**:
     - Opsi A (Otomatis): Pilih **Source: GitHub Actions** (workflow `.github/workflows/deploy-pages.yml` akan otomatis aktif).
     - Opsi B (Manual): Pilih **Source: Deploy from a branch**, Branch: `main` / `/(root)`.
   - Simpan. Dalam 1-2 menit, link website publik Anda akan aktif di:
     `https://<username-anda>.github.io/<nama-repo>/`

---

## 4. Menghubungkan Frontend GitHub Pages dengan Laptop Anda

1. Buka website Anda di browser (misal: `https://<username-anda>.github.io/<nama-repo>/`).
2. Klik tombol ikon **⚙️ (Pengaturan Server)** di pojok kanan atas header.
3. Masukkan **Public HTTPS URL** yang muncul saat Anda menjalankan `python run_public_tunnel.py` (contoh: `https://contoh-subdomain.trycloudflare.com`).
4. Klik **Uji Koneksi** lalu klik **Simpan & Terapkan**.
5. Selesai! Status koneksi akan berubah menjadi **Online (Hijau)** dan website siap digunakan oleh siapapun di internet.

---

## 5. Fitur Utama Antarmuka

- **Desain Monokrom / Hitam-Putih**: Sesuai estetika minimalis modern bernuansa pejuang lingkungan (*eco-warrior*).
- **Streaming SSE (Server-Sent Events)**: Jawaban asisten muncul kata demi kata secara instan.
- **Voice Recognition (STT)**: Tekan ikon mikrofon untuk berbicara dalam Bahasa Indonesia.
- **Text-to-Speech (TTS)**: Aktifkan ikon speaker di header untuk mendengarkan suara asisten membaca jawaban.
- **Quick Action Chips**: Akses instan ke topik-topik populer (Mangrove, Terumbu Karang, Bersih Pantai, Relawan, CSR, Gelang Komitmen, Chapter Regional).
- **Export Riwayat Chat**: Unduh catatan sesi percakapan dalam format file `.txt`.

---

## 🌿 Slogan Gerakan
*"Bukan Sekadar Bicara, Tapi Aksi Nyata"* — Seasoldier Indonesia
