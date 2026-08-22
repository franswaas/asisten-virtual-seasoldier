# Asisten Virtual Seasoldier Indonesia 🌊🌿
> **Action-Based Environmental Movement — Official Virtual Assistant**
> *Live Website (Firebase Hosting):* **[https://spotbersih-cfc15.web.app/](https://spotbersih-cfc15.web.app/)**
> *Live Website (GitHub Pages):* **[https://franswaas.github.io/asisten-virtual-seasoldier/](https://franswaas.github.io/asisten-virtual-seasoldier/)**

Asisten Virtual resmi berbasis **FastAPI / Firebase Cloud Functions + Groq LLM (High-Speed Inference) + Compact Smart RAG Engine** untuk menyajikan informasi resmi, terverifikasi, dan komprehensif seputar gerakan lingkungan hidup independen [Seasoldier.org](https://seasoldier.org/) yang didirikan oleh **Nadine Chandrawinata** dan **Dinni Septianingrum** pada 28 Maret 2015.

Antarmuka dirancang dengan tema **Hitam-Putih Murni (Pure Noir Minimalist — Chatwoot Style Architecture)** yang modern, responsif di HP/Desktop, berkecepatan tinggi, dan aman.

---

## 🌟 Fitur Unggulan

- 🧠 **Cerdas & Berbasis Data Resmi (Direct Smart RAG)**:
  - Mengintegrasikan basis data lengkap: Program Konservasi (#PohonUntukKehidupan, #KonservasiMangrove, Terumbu Karang Biorock, Blue Carbon NOAA/IAEA/World Bank), Aksi Sampah (#BersihkanWarisanKita, Pirolisis BBM, Ecobrick), Edukasi (Seasoldier Junior, Pondok Pemuda), Kemitraan CSR, Merchandise Gelang Komitmen, dan Direktori 21+ Chapter Daerah.
  - Memiliki catatan dinamis (*validation notice*) bahwa basis data divalidasi berkala dan menerima masukan pengguna.
- 🔥 **Serverless Cloud Ready (Google Firebase)**:
  - Frontend di-host di Firebase Hosting CDN super cepat.
  - Backend dapat dijalankan sebagai Firebase Cloud Functions Gen 2 (Python FastAPI) atau backend lokal/tunnel.
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
  - Kunci API Groq aman di serverless environment `.env` yang dilindungi `.gitignore` (tidak pernah terunggah ke GitHub).
  - Frontend murni klien statis yang tidak menyimpan kredensial sensitif.
  - Respon error backend disanitasi menyeluruh tanpa membocorkan rincian sistem.

---

## 📂 Struktur Proyek

```
Asisten Virtual Seasoldier/
├── firebase.json              # Konfigurasi Firebase Hosting & Cloud Functions
├── .firebaserc                # Target Project ID Firebase (spotbersih-cfc15)
├── deploy_firebase.bat        # Skrip 1-klik Windows untuk deploy ke Firebase
├── functions/                 # Backend Serverless Firebase Cloud Functions (Python Gen 2)
│   ├── main.py                # Cloud Function HTTPS entrypoint & FastAPI App
│   ├── config.py              # Konfigurasi system prompt & model
│   ├── retrieval.py           # RAG Engine (BM25 + TF-IDF)
│   ├── tools.py               # Helper tools & topic queries
│   ├── requirements.txt       # Dependensi Python untuk Firebase Functions
│   ├── .env.example           # Template environment variable
│   └── knowledge_base/
│       └── seasoldier_kb.txt  # Basis data resmi Seasoldier
├── frontend/                  # Antarmuka web monokrom (Firebase Hosting Public)
│   ├── index.html             # Antarmuka Chatwoot-style (SEO & Mobile Ready)
│   ├── style.css              # Styling Pure Noir Minimalist (100dvh + Safe Area + Markdown)
│   ├── app.js                 # Logika streaming SSE, Typewriter Queue, STT, TTS, & Auto-detect API
│   └── assets/
│       └── logo.jpg           # Logo resmi Seasoldier (Favicon & Avatar)
├── backend/                   # Standalone Python FastAPI Backend (Local Dev & Tunnel)
│   ├── config.py              # Konfigurasi lokal
│   ├── main.py                # Server FastAPI REST & SSE Streaming
│   ├── retrieval.py           # Custom Domain RAG Engine
│   └── requirements.txt       # Dependensi lokal
├── knowledge_base/
│   └── seasoldier_kb.txt      # Basis data utama
├── docs/
│   ├── panduan_firebase.md    # Panduan teknis lengkap migrasi & deployment Firebase
│   └── panduan_setup.md       # Panduan teknis setup lokal & Cloudflare Tunnel
└── README.md
```

---

## 🚀 Panduan Deployment Firebase

### 1. Deploy 1-Klik ke Firebase
Jalankan file batch **`deploy_firebase.bat`** atau ketik di terminal:
```bash
# Deploy Hosting + Cloud Functions
firebase deploy

# Atau deploy Frontend Hosting saja
firebase deploy --only hosting
```

Panduan selengkapnya dapat dibaca di: **[`docs/panduan_firebase.md`](docs/panduan_firebase.md)**.

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
