# Asisten Virtual Seasoldier Indonesia 🌊🌿
> **Action-Based Environmental Movement — Virtual Assistant**

Asisten Virtual berbasis **FastAPI + Groq LLM (Llama 3.3 70B) + Custom RAG Retrieval Engine** untuk menyajikan informasi resmi seputar program konservasi, aksi bersih pantai, edukasi lingkungan, kemitraan CSR, merchandise gelang komitmen, dan cara bergabung relawan (*Soldiers*) di 21+ chapter regional [Seasoldier.org](https://seasoldier.org/).

Antarmuka dirancang dengan tema **Hitam-Putih (Monochrome High-End Minimalist)** yang bersih, responsif, dan elegan.

---

## 🌟 Fitur Utama

- 🧠 **Cerdas & Akurat**: Menggunakan model AI canggih Llama 3.3 70B Versatile dengan basis data resmi Seasoldier Indonesia.
- ⚡ **Real-Time Streaming (SSE)**: Respon teks muncul token demi token tanpa jeda.
- 🎨 **Tampilan UI Hitam-Putih**: Estetika monokrom berkelas tinggi, modern, dan berkontras optimal.
- 🎙️ **Voice Input & Output**:
  - *Speech-to-Text* (Microphone Web Speech API bahasa Indonesia).
  - *Text-to-Speech* (Suara asisten membacakan jawaban).
- ⚙️ **Dukungan GitHub Pages & Backend Lokal**: Dilengkapi modal pengaturan URL backend dinamis sehingga frontend dapat di-hosting di GitHub Pages sementara backend berjalan di laptop.
- 💾 **Export & Feedback**: Fitur download riwayat chat (.txt) dan rating masukan (thumbs up/down).

---

## 📂 Struktur Proyek

```
Asisten Virtual Seasoldier/
├── backend/
│   ├── config.py              # Konfigurasi, system prompt, model AI, dan CORS
│   ├── retrieval.py           # Custom TF-IDF/BM25 domain RAG engine
│   ├── tools.py               # OpenAI/Groq function calling tools
│   ├── hooks.py               # Analytics, logging, dan tracking sesi
│   ├── main.py                # FastAPI REST & SSE Streaming Server
│   ├── requirements.txt       # Dependensi Python
│   └── .env                   # Environment API key & setting
├── frontend/
│   ├── index.html             # Antarmuka web monokrom
│   ├── style.css              # Styling Black & White Luxury Minimalist
│   └── app.js                 # Logika streaming SSE, STT, TTS, dan koneksi
├── knowledge_base/
│   └── seasoldier_kb.txt      # Data resmi profil, visi-misi, program & chapter
├── docs/
│   └── panduan_setup.md       # Panduan lengkap setup lokal & tunneling
└── README.md
```

---

## 🚀 Cara Menjalankan Cepat

### 1. Jalankan Backend (Laptop)
```bash
cd backend
pip install -r requirements.txt
python main.py
```
Akses langsung di browser: **`http://localhost:4001`**

### 2. Hubungkan ke GitHub Pages
Lihat panduan lengkap di [`docs/panduan_setup.md`](docs/panduan_setup.md) untuk langkah-langkah *deploy* frontend ke GitHub Pages dan menghubungkan *tunneling* (Cloudflare/LocalTunnel/Ngrok) ke backend di laptop Anda.

---

## 🌿 Slogan Gerakan
*"Bukan Sekadar Bicara, Tapi Aksi Nyata"* — Seasoldier Indonesia
