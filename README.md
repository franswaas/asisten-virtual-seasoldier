# Asisten Virtual Seasoldier Indonesia 🌊🌿
> **Action-Based Environmental Movement — Official Virtual Assistant**
> *Live Website:* **[https://franswaas.github.io/asisten-virtual-seasoldier/](https://franswaas.github.io/asisten-virtual-seasoldier/)**

Asisten Virtual resmi berbasis **FastAPI + Groq LLM (High-Speed Inference) + Compact Smart RAG Engine** untuk menyajikan informasi resmi, terverifikasi, dan komprehensif seputar gerakan lingkungan hidup independen [Seasoldier.org](https://seasoldier.org/) yang didirikan oleh **Nadine Chandrawinata** dan **Dinni Septianingrum** pada 28 Maret 2015.

Antarmuka dirancang dengan tema **Hitam-Putih Murni (Pure Noir Minimalist — Chatwoot Style Architecture)** yang modern, responsif di HP/Desktop, berkecepatan tinggi, dan aman.

---

## 🌟 Fitur Unggulan

- 🧠 **Cerdas & Berbasis Data Resmi (Direct Smart RAG)**:
  - Mengintegrasikan basis data lengkap: Program Konservasi (#PohonUntukKehidupan, #KonservasiMangrove, Terumbu Karang Biorock, Blue Carbon NOAA/IAEA/World Bank), Aksi Sampah (#BersihkanWarisanKita, Pirolisis BBM, Ecobrick), Edukasi (Seasoldier Junior, Pondok Pemuda), Kemitraan CSR, Merchandise Gelang Komitmen, dan Direktori 21+ Chapter Daerah.
  - Memiliki catatan dinamis (*validation notice*) bahwa basis data divalidasi berkala dan menerima masukan pengguna.
- ⚡ **Respon Instan Tanpa Delay (<1.2 detik)**:
  - Menggunakan pipeline *High-Density Compact Prompt* dan *Smart History Pruning* sehingga kebal terhadap pembatasan kuota token (*rate limit free*) dan selalu merespon cepat untuk pertanyaan ke-1, ke-2, hingga seterusnya.
- 🎬 **Animasi Mengetik Halus (*Fluid Typewriter Streamer Queue*)**:
  - Teks mengalir tenang dan teratur (~30–40ms per step) pada HP maupun laptop, tanpa efek berkedip atau bertumpuk.
- 📱 **Mobile-First & Responsif (100dvh + Safe Area)**:
  - Kolom pesan tidak terpotong oleh bilah navigasi Android/iOS berkat *Dynamic Viewport Height* (`100dvh`) dan `env(safe-area-inset-bottom)`.
  - Akselerasi perangkat keras (*GPU compositing*) untuk performa mulus di browser seluler.
- 🎙️ **Interaksi Suara Dua Arah (Voice STT & TTS)**:
  - *Speech-to-Text* (Input suara langsung via mikrofon Web Speech API Bahasa Indonesia).
  - *Text-to-Speech* (Asisten dapat membacakan jawaban dengan intonasi ramah).
- 🔒 **Keamanan & Privasi Maksimal (Zero Leak Security)**:
  - Kunci API Groq aman di laptop via `.env` yang dilindungi `.gitignore` (tidak pernah terunggah ke GitHub).
  - Frontend murni klien statis yang tidak menyimpan kredensial sensitif.
  - Respon error backend disanitasi menyeluruh tanpa membocorkan rincian sistem.
- ☁️ **Akses Publik 1-Klik (Cloudflare Tunnel Daemon)**:
  - Dilengkapi skrip otomatisasi Python & batch file yang membuka tunnel HTTPS publik berkecepatan tinggi tanpa perlu daftar akun atau instalasi rumit.

---

## 📂 Struktur Proyek

```
Asisten Virtual Seasoldier/
├── backend/
│   ├── config.py              # Konfigurasi, system prompt berdensitas tinggi, dan model LLM
│   ├── main.py                # Server FastAPI REST & SSE Streaming + Sanitasi Kata
│   ├── retrieval.py           # Custom Domain RAG Engine (BM25/TF-IDF)
│   ├── tools.py               # Tool helper & knowledge retrieval
│   ├── hooks.py               # Logging percakapan, analitik, dan tracking error
│   ├── requirements.txt       # Dependensi Python backend
│   └── .env                   # Kunci API Groq (Aman di lokal, diabaikan Git)
├── frontend/
│   ├── index.html             # Antarmuka web monokrom Chatwoot-style (SEO & Mobile Ready)
│   ├── style.css              # Styling Pure Noir Minimalist (100dvh + Safe Area + Markdown)
│   ├── app.js                 # Logika streaming SSE, Typewriter Queue, STT, TTS, dan Auto-scroll
│   └── assets/
│       └── logo.jpg           # Logo resmi Seasoldier (Favicon & Avatar)
├── knowledge_base/
│   └── seasoldier_kb.txt      # Basis data lengkap & terverifikasi (Sains, Konservasi & Chapter)
├── docs/
│   └── panduan_setup.md       # Panduan teknis lengkap & troubleshooting
├── run_public_tunnel.py       # Skrip 1-klik untuk memulai backend & secure Cloudflare HTTPS tunnel
├── start_public_server.bat    # Windows Batch launcher untuk kemudahan menjalankan server
├── .gitignore                 # Proteksi file rahasia (.env, sessions, logs, cache)
└── README.md
```

---

## 🚀 Panduan Menjalankan Sistem

### Opsi A: 1-Klik Jalankan Server Publik (Rekomendasi)
Cukup klik dua kali file **`start_public_server.bat`** atau jalankan perintah:
```bash
python run_public_tunnel.py
```
Skrip ini akan secara otomatis:
1. Menjalankan backend FastAPI di port `4001`.
2. Menghubungkan tunnel secure HTTPS publik via Cloudflare.
3. Menampilkan **Public HTTPS URL** yang siap dimasukkan ke pengaturan website GitHub Pages.

---

### Opsi B: Jalankan Backend Lokal Saja
```bash
# 1. Masuk ke direktori backend
cd backend

# 2. Instal dependensi
pip install -r requirements.txt

# 3. Jalankan server FastAPI
python main.py
```
Server backend lokal akan aktif di: `http://localhost:4001`

---

## 🌐 Menghubungkan ke GitHub Pages
1. Buka website: **[https://franswaas.github.io/asisten-virtual-seasoldier/](https://franswaas.github.io/asisten-virtual-seasoldier/)**
2. Klik tombol **Pengaturan (⚙️)** di pojok kanan atas antarmuka.
3. Masukkan **Public HTTPS URL** dari terminal laptop Anda (contoh: `https://xxxx.trycloudflare.com`).
4. Klik **Uji Koneksi** lalu klik **Simpan & Terapkan**.
5. Asisten Virtual Seasoldier langsung **Online** dan dapat digunakan oleh siapa saja di seluruh dunia!

---

## 🛡️ Aturan Identitas & Kata Terlarang (Strict Rule)
Sesuai arahan resmi:
- Dilarang keras menggunakan kata: **`"yayasan"`**, **`"ai bot"`**, atau **`"bot"`**.
- Selalu sebut organisasi sebagai: **Seasoldier**, **Seasoldier Indonesia**, atau **gerakan Seasoldier**.
- Selalu sebut asisten sebagai: **Asisten Virtual Seasoldier** atau **Asisten Seasoldier**.

---

## 🌿 Slogan & Filosofi Gerakan
> *"Bukan Sekadar Bicara, Tapi Aksi Nyata"* — **Seasoldier Indonesia**  
> *"80% sampah laut berasal dari darat, menjaga lingkungan adalah tanggung jawab kita bersama."*
