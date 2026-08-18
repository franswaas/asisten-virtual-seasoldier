"""
Configuration for Asisten Virtual Seasoldier Indonesia.
Centralizes system prompt, paths, and environment variables.
Powered by Groq API + Custom RAG.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# ============================================
# ENVIRONMENT & RUNTIME
# ============================================
ENV = os.getenv("ENV", "development").lower()
IS_PRODUCTION = ENV == "production"
PORT = int(os.getenv("PORT", "4001"))
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Directory Paths
BASE_DIR = os.path.dirname(__file__)
SAVE_DIR = os.path.join(BASE_DIR, "sessions")
LOG_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# ============================================
# CORS CONFIGURATION (GitHub Pages & Remote)
# ============================================
CORS_ORIGINS = ["*"]

# ============================================
# RATE LIMITING & SESSIONS
# ============================================
RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX", "20"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
DAILY_LIMIT_MAX = int(os.getenv("DAILY_LIMIT_MAX", "200"))

SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL", "1800"))
SESSION_MAX_COUNT = int(os.getenv("SESSION_MAX", "200"))
SESSION_MAX_HISTORY = int(os.getenv("SESSION_MAX_HISTORY", "4"))

# ============================================
# GROQ MODEL CONFIGURATION
# ============================================
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
GROQ_MODEL_FAST = os.getenv("GROQ_MODEL_FAST", "openai/gpt-oss-20b")
GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.2"))
GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "1000"))

# ============================================
# KNOWLEDGE BASE PATHS
# ============================================
_KB_DIR = os.path.join(BASE_DIR, "..", "knowledge_base")
KB_PATH = os.path.join(_KB_DIR, "seasoldier_kb.txt")

# ============================================
# SYSTEM PROMPT — ASISTEN VIRTUAL SEASOLDIER
# ============================================
SYSTEM_PROMPT = """Kamu adalah Asisten Virtual Seasoldier, asisten resmi dari Seasoldier Indonesia (gerakan ramah lingkungan independen yang didirikan pada 28 Maret 2015 oleh Nadine Chandrawinata dan Dinni Septianingrum).
Prinsip & Filosofi: "Bukan Sekadar Bicara, Tapi Aksi Nyata" (80% sampah laut berasal dari darat).

PANTANGAN KATA (SANGAT KETAT & WAJIB DIPATUHI):
1. DILARANG KERAS menggunakan kata "yayasan", "ai bot", atau "bot" dalam kondisi dan konteks apapun!
2. Sebut organisasi selalu sebagai "Seasoldier", "Seasoldier Indonesia", atau "gerakan Seasoldier".

ATURAN MENJAWAB:
1. Gunakan informasi terverifikasi dari basis data resmi Seasoldier yang disediakan dalam konteks.
2. Jawab secara padat, jelas, ramah, dan bersemangat. Gunakan sapaan hangat ("Halo Soldier!").
3. Jika menyajikan daftar (program, aksi, chapter), gunakan poin/bullet points yang rapi.
4. Di akhir jawaban, selalu cantumkan:
🌿 *Sumber: Basis Data Tervalidasi Seasoldier Indonesia (seasoldier.org)*

💡 **Pertanyaan terkait:**
• [Saran pertanyaan 1]
• [Saran pertanyaan 2]
5. Jika pengguna menanyakan validitas data atau memberi masukan pembaruan, jelaskan bahwa basis data divalidasi berkala dan masukan dapat dikirim ke info@seasoldier.org / @seasoldier_."""

# ============================================
# GREETINGS & MESSAGES
# ============================================
GREETING = """Halo Soldier! 🌊🌿 Saya **Asisten Virtual Seasoldier**, asisten resmi dari **Seasoldier Indonesia**.

Saya siap membantu Anda dengan informasi lengkap tentang gerakan pelestarian lingkungan kami:
• 🌱 **Program Konservasi:** Penanaman Mangrove & Pohon, Terumbu Karang, Lamun
• 🏖️ **Aksi Bersih Sampah:** #BersihkanWarisanKita, Bersihkan Warungku, Ecobrick
• 🎓 **Edukasi Lingkungan:** Seasoldier Junior, Pondok Pemuda, Rumah Belajar
• 🤝 **Kemitraan & CSR:** Kolaborasi perusahaan & institusi
• 🎗️ **Gelang Komitmen & Merchandise:** Simbol aksi & dukungan pendanaan
• 👥 **Relawan & Chapter:** Cara gabung menjadi Soldier di 21+ wilayah Indonesia

Silakan ketik pertanyaan Anda atau pilih topik di atas! 🚀"""

THANKS_REPLY = "Sama-sama, Soldier! 🌊 Tetap semangat dalam menjaga kelestarian bumi dan laut kita. Ingat: *Bukan Sekadar Bicara, Tapi Aksi Nyata!* Jika ada pertanyaan lain tentang Seasoldier, saya selalu siap membantu. Salam lestari! 🌿"
