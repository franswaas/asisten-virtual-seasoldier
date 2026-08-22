"""
Custom Tools for Asisten Virtual Seasoldier.
Callable by Groq LLM via OpenAI-compatible Function Calling format.
"""

import os
from retrieval import SeasoldierKBRetrieval
from hooks import log_tool_call

# ============================================
# SINGLETON RETRIEVAL ENGINE
# ============================================
_engine: SeasoldierKBRetrieval | None = None


def get_engine() -> SeasoldierKBRetrieval:
    """Get or instantiate the singleton retrieval engine for Seasoldier KB."""
    global _engine
    if _engine is None:
        from config import KB_PATH
        _engine = SeasoldierKBRetrieval(KB_PATH)
    return _engine


# ============================================
# TOOL 1: search_knowledge_base
# ============================================
def search_knowledge_base(query: str, top_k: int = 6) -> str:
    """Cari informasi resmi dari knowledge base Seasoldier Indonesia.

    Gunakan tool ini untuk mencari informasi seputar program konservasi (mangrove, terumbu karang, pohon),
    aksi bersih sampah (#BersihkanWarisanKita, Bersihkan Warungku, Ecobrick), edukasi (Seasoldier Junior,
    Pondok Pemuda), kemitraan CSR, merchandise gelang komitmen, cara gabung relawan (Soldier),
    dan kontak chapter regional.

    Args:
        query: Kata kunci pencarian yang relevan. Contoh: 'penanaman mangrove', 'cara jadi relawan',
               'harga gelang komitmen', 'program CSR perusahaan', 'chapter Bali'
        top_k: Jumlah hasil pencarian (default: 6, max: 10)

    Returns:
        Teks konteks dari knowledge base resmi yang relevan.
    """
    engine = get_engine()
    top_k = min(max(top_k, 1), 10)

    try:
        results = engine.search(query, top_k)
    except Exception as e:
        log_tool_call("search_knowledge_base", {"query": query, "top_k": top_k}, 0)
        return f"Terjadi kesalahan saat mencari di knowledge base: {e}"

    if not results:
        res = "Tidak ditemukan informasi yang sesuai dalam knowledge base Seasoldier. Silakan coba kata kunci lain."
        log_tool_call("search_knowledge_base", {"query": query, "top_k": top_k}, len(res))
        return res

    sections: list[str] = []
    for i, r in enumerate(results):
        header = f"[Bagian {i + 1} | Skor: {r.score:.1f}"
        if r.section_title:
            header += f" | {r.section_title}"
        header += "]"
        sections.append(f"{header}\n{r.chunk}")

    result_text = "\n\n---\n\n".join(sections)
    log_tool_call("search_knowledge_base", {"query": query, "top_k": top_k}, len(result_text))
    return result_text


# ============================================
# TOOL 2: list_available_topics
# ============================================
def list_available_topics() -> str:
    """Daftar topik dan cakupan informasi yang tersedia dalam Knowledge Base Seasoldier.

    Returns:
        Ringkasan kategori informasi yang dapat ditanyakan pengguna.
    """
    topics = """Kategori Informasi yang Tersedia di Knowledge Base Seasoldier:
1. 🏛️ **Musyawarah Nasional (MUNAS) III & Seasoldier Xperience:** Rangkaian Munas III Semarang (21-23 Agustus 2026), Workshop "Managing Green Organization for Green Jobs Opportunities", Talkshow "Gaya Hidup Berkelanjutan: Tren atau Kebutuhan?", Factory Visit Oemah Herborist, Aksi Tanam Mangrove Pantai Mangunharjo, Tata Tertib, Tradisi Snack Exchange, & Kontak Panitia.
2. 👥 **Profil Tokoh Pendiri & Kolaborator Lingkungan:** Nadine Chandrawinata (@nadinelist - Founder), Dinni Septianingrum (@dinni_s - Co-Founder & Head of Seasoldier), Ramon Y. Tungka (@ramonytungka - Aktor & Outdoor Adventurer), Medina Kamil (@medinakamil - TV Presenter Jejak Petualang & Outdoor Enthusiast).
3. 🌱 **Konservasi & Reboisasi:** Penanaman Mangrove (#PohonUntukKehidupan, #KonservasiMangrove), Transplantasi Terumbu Karang, Padang Lamun, Konservasi Bambu, 43 Titik Konservasi Nasional.
4. 🏖️ **Aksi Bersih Sampah & Lingkungan:** #BersihkanWarisanKita (Beach & Coastal Clean-up), Program Bersihkan Warungku (mentoring UMKM), Pelatihan Ecobrick.
5. 🎓 **Edukasi & Generasi Muda:** Seasoldier Junior (Sekolah & Anak), Pondok Pemuda (Youth Sustainability Camp), Rumah Belajar Pesisir.
6. 📢 **Kampanye & Advokasi:** #BraniGundul, #DolphinNotClown (penolakan sirkus lumba-lumba), #SmartTraveling, #MenanamMelawanKepunahan.
7. 🤝 **Kemitraan CSR & Korporasi:** Penanaman mangrove skala besar, Employee Volunteering, CSR multi-tahun, Waste Management Workshop, Laporan ESG & SDGs.
8. 🎗️ **Merchandise & Pendanaan:** Gelang Komitmen Seasoldier (daur ulang), Tumbler stainless, Tote bag, Kaos organik, Donasi #KuponUntukAksi.
9. 👥 **Relawan (Soldier) & 21+ Chapter:** Syarat & cara bergabung relawan, sebaran chapter daerah di seluruh Indonesia (Jakarta, Bali, Bandung, Surabaya, Medan, Makassar, Ambon, dll.).
10. 📞 **Kontak & Media Sosial:** Instagram resmi @seasoldier_, website seasoldier.org, email info & partnership, WhatsApp hotline.
"""
    log_tool_call("list_available_topics", {}, len(topics))
    return topics


# ============================================
# TOOL 3: get_program_detail
# ============================================
def get_program_detail(program_name: str) -> str:
    """Ambil rincian spesifik mengenai salah satu program unggulan Seasoldier.

    Args:
        program_name: Nama program (contoh: 'mangrove', 'clean-up', 'junior', 'pondok pemuda', 'warungku', 'ecobrick', 'gelang', 'dolphin')
    """
    engine = get_engine()
    results = engine.search(program_name, top_k=3)
    if not results:
        return f"Informasi detail tentang program '{program_name}' belum ditemukan dalam basis data."
    return "\n\n".join([r.chunk for r in results])


# ============================================
# TOOL 4: get_chapter_info
# ============================================
def get_chapter_info(region: str) -> str:
    """Ambil informasi mengenai Chapter Regional Seasoldier di wilayah tertentu.

    Args:
        region: Nama kota atau provinsi (contoh: 'Jakarta', 'Bandung', 'Bali', 'Surabaya', 'Medan', 'Makassar', 'Ambon', 'Lombok')
    """
    engine = get_engine()
    results = engine.search(f"chapter {region}", top_k=3)
    if not results:
        return f"Chapter Seasoldier di wilayah '{region}' dapat dihubungi melalui Instagram resmi @seasoldier_."
    return "\n\n".join([r.chunk for r in results])
