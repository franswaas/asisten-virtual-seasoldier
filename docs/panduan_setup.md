# Panduan Setup & Akses Publik Asisten Virtual Seasoldier

Dokumen ini menjelaskan langkah-langkah menjalankan backend di laptop secara lokal, melakukan deployment frontend ke **Firebase Hosting** dan **GitHub Pages**, serta menghubungkan keduanya via **Cloudflare HTTPS Tunnel** sehingga sistem dapat diakses secara publik oleh siapapun di internet.

---

## 🏛️ Arsitektur Sistem

```
[Pengguna Publik / HP / Laptop]
       │
       ▼ (HTTPS)
[Frontend Statis: Firebase Hosting CDN]
https://asisten-seasoldier.web.app/ (atau GitHub Pages)
       │
       ▼ (Permintaan Streaming SSE / REST)
[Cloudflare Secure HTTPS Tunnel]
https://xxxx.trycloudflare.com
       │
       ▼ (Local Port 4001)
[Backend Laptop: FastAPI + Python 3.10+]
       │
       ├──► [Groq AI LLM (openai/gpt-oss-120b)]
       └──► [Knowledge Base Seasoldier (BM25/TF-IDF Compact Smart RAG)]
```

---

## 1. Menjalankan Backend & Tunnel Publik (1-Klik)

Kami telah menyediakan script otomatisasi untuk memulai server FastAPI dan membuka tunnel publik sekaligus:

### Opsi A: Menggunakan Script Python (Otomatis & Terintegrasi)
Jalankan perintah berikut di root folder proyek:
```powershell
python run_public_tunnel.py
```
*Skrip ini akan memeriksa binary Cloudflare, memulai server FastAPI di port 4001, dan langsung menampilkan **Public HTTPS URL** di layar terminal.*

### Opsi B: Menggunakan File Batch Windows
Buka Windows Explorer dan **Double Click** pada file:
👉 **`start_public_server.bat`**

---

## 2. Menghubungkan Backend ke Website Firebase / HP

Ada 2 cara sangat mudah untuk menghubungkan backend ke website:

### Opsi 1: Menggunakan Link Auto-Connect (Paling Mudah untuk HP & Laptop) ⭐
1. Saat menjalankan `start_public_server.bat` atau `python run_public_tunnel.py`, terminal akan menampilkan:
   ```
   📱 LINK AUTO-CONNECT (HP & LAPTOP):
      👉 https://asisten-seasoldier.web.app/?backend=https://xxxx.trycloudflare.com
   ```
2. **Di HP**: Salin/kirim link tersebut ke HP (via WhatsApp, Telegram, atau scan). Begitu dibuka di browser HP, sistem akan **langsung otomatis terhubung 100% ONLINE** tanpa perlu input manual!
3. **Di Laptop**: Browser laptop akan otomatis terbuka ke link tersebut dan langsung terhubung.

---

### Opsi 2: Konfigurasi Manual via Menu Pengaturan (⚙️)
1. Buka website: **[https://asisten-seasoldier.web.app/](https://asisten-seasoldier.web.app/)**
2. Klik tombol ikon **⚙️ (Pengaturan Server)** di pojok kanan atas.
3. Masukkan **Public HTTPS URL** yang tampil di terminal Anda (contoh: `https://xxxx.trycloudflare.com`).
4. Klik **Uji Koneksi** lalu klik **Simpan & Terapkan**.
5. Selesai! Indikator status akan berubah menjadi **Online (Hijau)** dan asisten siap digunakan.

---

## 3. Fitur Utama & Keunggulan Sistem

- **Tampilan Pure Noir Minimalist (Hitam-Putih)**: Desain modern, elegan, dan kontras tinggi sesuai nilai pejuang lingkungan.
- **Respon Cepat Tanpa Pembatasan Token (<1.2s)**: Menggunakan prompt berdensitas tinggi dan pemangkasan riwayat percakapan sehingga kebal terhadap *rate limit* untuk pertanyaan beruntun.
- **Animasi Pengetikan Halus (*Typewriter Streamer Queue*)**: Teks mengalir teratur dan nyaman dibaca tanpa kedipan atau teks bertumpuk di HP maupun laptop.
- **Desain Khusus Mobile (100dvh + Safe Area Inset)**: Kolom pengetikan pesan tidak akan terpotong oleh tombol navigasi sistem Android/iOS.
- **Interaksi Suara (STT & TTS)**: Mendukung input suara mikrofon dan pembacaan teks otomatis dalam Bahasa Indonesia.
- **Privasi & Keamanan Data (Zero Leak)**: API key tersimpan aman di `.env` lokal dan tidak pernah terunggah ke GitHub.

---

## 4. Troubleshooting & Solusi Kendala

| Kendala | Penyebab | Solusi |
|---|---|---|
| **Status Offline / Gagal Konek** | Terminal laptop tertutup atau URL tunnel berganti | Jalankan `start_public_server.bat` dan perbarui URL di menu Pengaturan (⚙️). |
| **Pertanyaan Beruntun Lambat** | Kuota token berlebih pada riwayat lama | Sistem telah menerapkan pemangkasan riwayat otomatis (*pruned history*). |
| **Layar HP Terpotong** | Browser mobile belum refresh cache | Lakukan *hard reload* pada browser HP atau buka di tab incognito. |

---

## 🌿 Slogan Gerakan
> *"Bukan Sekadar Bicara, Tapi Aksi Nyata"* — **Seasoldier Indonesia**
