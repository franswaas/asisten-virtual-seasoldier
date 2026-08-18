"""
Enhanced TF-IDF & BM25 Knowledge Base Retrieval Engine.
Tailored for Seasoldier environmental conservation domain.
"""

import math
import os
import re
from dataclasses import dataclass

# ============================================
# DATA STRUCTURES
# ============================================
@dataclass
class SearchResult:
    chunk: str
    index: int
    score: float
    section_title: str = ""


# ============================================
# DOMAIN SYNONYMS & EXPANSIONS
# ============================================
SYNONYMS: dict[str, list[str]] = {
    # Konservasi & Lingkungan
    "mangrove": ["bakau", "hutan bakau", "konservasi mangrove", "pohon untuk kehidupan", "blue carbon", "bibit", "zonasi mangrove", "rhizophora", "avicennia", "sonneratia", "bruguiera", "lindungihutan", "mangrove tag", "mangrove data", "eiger"],
    "bakau": ["mangrove", "hutan mangrove", "konservasi mangrove", "pohon", "rhizophora", "akar tunjang"],
    "zonasi": ["zonasi mangrove", "zona terdepan", "zona tengah", "zona belakang", "rhizophora", "avicennia", "sonneratia", "bruguiera", "nipah"],
    "akar": ["akar tunjang", "akar napas", "akar lutut", "pneumatophores", "stilt roots", "morfologi mangrove"],
    "eiger": ["eiger adventure", "fungsi hutan mangrove", "11 fungsi mangrove", "mitigasi abrasi"],
    "mangrovedata": ["mangrove data", "konservasi melalui data", "5 upaya penting", "basis data mangrove"],
    "lindungihutan": ["lindungihutan", "manfaat konservasi mangrove", "program konservasi", "survival rate", "3.36 juta hektar"],
    "mangrovetag": ["mangrove tag", "zonasi mangrove", "emr", "ecological mangrove restoration", "propagula", "vivipar"],
    "karang": ["terumbu karang", "coral", "transplantasi", "terumbu", "lamun", "seagrass", "biota", "biorock", "zooxanthellae", "coral bleaching", "polip", "coral triangle", "noaa", "ssi", "iar indonesia"],
    "coral": ["terumbu karang", "transplantasi karang", "lamun", "biorock", "coral reef", "coral bleaching", "edu'coral", "noaa"],
    "terumbu": ["terumbu karang", "coral reef", "transplantasi", "biorock", "ekowisata karang", "polip", "zooxanthellae"],
    "biorock": ["biorock indonesia", "mineral accretion", "arus listrik", "restorasi karang", "pemuteran", "bangsring", "tiga warna", "ekowisata"],
    "bleaching": ["pemutihan karang", "coral bleaching", "zooxanthellae", "suhu laut", "marine heatwaves", "perubahan iklim"],
    "ssi": ["scuba schools international", "divessi", "edu'coral", "the coral planters", "pendidikan terumbu karang", "eco-diver"],
    "iar": ["iar indonesia", "yiari", "inisiasi alam rehabilitasi indonesia", "coral triangle", "raja ampat", "wakatobi", "bunaken", "alor"],
    "ekowisata": ["ekowisata karang", "biorock", "wisata bahari", "dive guide", "smart traveling", "pemuteran", "marine protected areas", "mpa"],
    "lamun": ["seagrass", "padang lamun", "karbon biru", "biota laut"],
    "pohon": ["pohon untuk kehidupan", "reboisasi", "penanaman", "bambu", "konservasi"],
    "bambu": ["konservasi bambu", "tangkapan air", "lereng", "erosi"],
    
    # Sampah & Aksi
    "sampah": ["plastik", "bersihkan warisankita", "clean-up", "beach cleanup", "ecobrick", "limbah", "bersihkan warungku", "manajemen sampah", "pemilahan"],
    "plastik": ["sampah plastik", "botol", "kantong kresek", "sedotan", "residu", "ecobrick", "jenis plastik", "resin", "daur ulang", "pirolisis"],
    "cleanup": ["clean-up", "beach cleanup", "bersih pantai", "bersihkan warisankita", "pesisir"],
    "ecobrick": ["eco brick", "residu plastik", "pelatihan ecobrick", "daur ulang"],
    "warung": ["bersihkan warungku", "umkm", "warung makan", "mentoring sampah"],
    "pirolisis": ["konversi bbm", "minyak bakar", "reaktor", "energi alternatif", "iec", "bbm plas"],
    "bbm": ["pirolisis", "bbm plas", "konversi plastik bbm", "ipst asari", "bahan bakar"],
    "daur": ["daur ulang", "recycling", "universal eco", "peletisasi", "pencacahan", "sorting"],
    "biodegradable": ["bioplastik", "pla", "pha", "pbat", "pbs", "pslh ugm", "oxo-degradable", "oxium"],
    "edukasi": ["sekolah", "waste4change", "akabis", "piket", "o-soji", "seasoldier junior", "plh"],
    "chandra": ["chandra asri", "9 tips pengolahan", "operasi semut", "circlo", "aspal plastik", "ipst asari"],
    "wwf": ["plastic smart cities", "wwf indonesia", "aksi", "ancaman plastik", "mikroplastik"],
    "wri": ["wri indonesia", "nol-sampah plastik 2040", "ekonomi sirkular", "epr", "perpres 83/2018"],
    "ugm": ["pslh ugm", "biodegradabilitas", "oxium", "mikroplastik", "pla", "pha"],
    "universal": ["universal eco", "proses daur ulang", "washing", "shredding", "sorting"],
    "iec": ["indonesia environment & energy center", "pirolisis", "konversi bbm", "7 jenis plastik"],
    
    # Relawan & Keanggotaan
    "relawan": ["soldier", "volunteer", "gabung", "daftar", "pendaftaran", "rekrutmen", "komunitas"],
    "soldier": ["relawan", "volunteer", "seasoldier", "pejuang lingkungan"],
    "volunteer": ["relawan", "soldier", "gabung", "daftar"],
    "gabung": ["daftar", "registrasi", "relawan", "volunteer", "chapter", "open recruitment"],
    "daftar": ["gabung", "registrasi", "formulir", "relawan", "soldier"],
    
    # Tokoh & Pendiri
    "nadine": ["nadine chandrawinata", "founder", "pendiri", "putri indonesia", "inisiator"],
    "dinni": ["dinni septianingrum", "co-founder", "head of seasoldier", "pendiri"],
    "pendiri": ["nadine chandrawinata", "dinni septianingrum", "founder", "inisiator", "sejarah"],
    "founder": ["nadine chandrawinata", "dinni septianingrum", "pendiri"],
    
    # Edukasi & Program
    "junior": ["seasoldier junior", "edukasi anak", "sekolah", "tk", "sd", "smp"],
    "pemuda": ["pondok pemuda", "youth camp", "leadership", "mahasiswa"],
    "belajar": ["rumah belajar", "anak pesisir", "buku", "perkampungan nelayan"],
    "lumba": ["dolphin not clown", "dolphins", "sirkus", "atraksi", "mamalia laut"],
    "dolphin": ["lumba-lumba", "dolphin not clown", "sirkus keliling"],
    "gundul": ["branigundul", "brani gundul", "komitmen"],
    "traveling": ["smart traveling", "smarttraveling", "responsible traveler", "wisata ramah lingkungan"],
    
    # Kemitraan & Merchandise
    "csr": ["kemitraan", "corporate", "kolaborasi", "perusahaan", "sponsorship", "employee volunteering", "managed csr", "esg"],
    "kemitraan": ["csr", "partnership", "kolaborasi", "kerjasama", "proposal", "managed csr"],
    "gelang": ["gelang komitmen", "bracelet", "merchandise", "simbol aksi", "daur ulang", "store"],
    "merchandise": ["gelang", "tumbler", "tote bag", "kaos", "t-shirt", "store", "toko"],
    "toko": ["store", "merchandise", "gelang", "tumbler", "kaos", "beli", "pesan"],
    "rejuve": ["re.juve", "kemitraan csr", "bring back your empty rejuve bottles", "towards zero waste", "donasi mangrove"],
    "untar": ["universitas tarumanagara", "pkm", "tanjung pasir", "kampus", "pengabdian masyarakat"],
    "unesa": ["universitas negeri surabaya", "studi independen", "wonorejo", "magang"],

    # Penghargaan & Metrik
    "penghargaan": ["kartini award", "ra kartini", "prestasi", "rekognisi", "inspiring celebrity", "award"],
    "kartini": ["ra kartini", "penghargaan", "nadine chandrawinata", "inspiring celebrity"],
    "sdgs": ["sustainable development goals", "sdg", "tujuan pembangunan berkelanjutan", "esg", "blue carbon"],
    "monitoring": ["survival rate", "pemantauan", "kelulusan hidup", "laporan berkala", "evaluasi"],

    # Blue Carbon & Referensi Ilmiah Global
    "blue": ["blue carbon", "karbon biru", "sekuestrasi", "sedimen", "noaa", "iaea", "world bank", "mangrove", "lamun"],
    "carbon": ["blue carbon", "karbon biru", "sekuestrasi", "emisi co2", "cadangan karbon", "sedimen anaerobik"],
    "karbon": ["blue carbon", "karbon biru", "sekuestrasi", "sedimen", "noaa", "iaea", "world bank", "problue"],
    "noaa": ["national oceanic and atmospheric administration", "blue carbon", "sekuestrasi mangrove", "lahan basah"],
    "iaea": ["international atomic energy agency", "teknologi nuklir", "isotop", "timbal-210", "karbon-14", "ndcs"],
    "bank": ["world bank", "bank dunia", "problue", "changing wealth of nations", "kredit karbon biru"],
    "sedimen": ["lumpur", "dasar laut", "anaerobik", "kedalaman 6 meter", "blue carbon", "penyimpanan karbon"],
    "isotop": ["iaea", "teknologi nuklir", "isotopic fingerprinting", "pelacakan sumber karbon", "timbal-210"],

    # Chapter & Wilayah
    "chapter": ["regional", "wilayah", "cabang", "kota", "koordinator", "lokasi"],
    "daerah": ["chapter", "regional", "wilayah", "lokasi", "cabang"],
    "bali": ["denpasar", "sanur", "serangan", "tanjung benoa", "chapter bali"],
    "jakarta": ["jabodetabek", "twa angke kapuk", "pulau untung jawa", "kepulauan seribu", "chapter jakarta"],
    "bandung": ["jawa barat", "chapter bandung"],
    "surabaya": ["gresik", "jawa timur", "wonorejo", "ekowisata mangrove", "chapter surabaya"],
    "semarang": ["jawa tengah", "pantai mangunharjo", "tambakrejo", "cemara brebes", "jepara", "chapter semarang"],
    "mempawah": ["kalimantan barat", "konservasi mangrove mempawah", "pontianak"],
    "likupang": ["sulawesi utara", "manado", "kek bahari", "pesisir likupang"],
    "makassar": ["sulawesi selatan", "chapter makassar"],
    "ambon": ["maluku", "chapter ambon"],
    "kontak": ["email", "instagram", "whatsapp", "telepon", "hubungi", "alamat", "sosial media"],
}

STOP_WORDS = {
    "yang", "di", "ke", "dari", "pada", "dalam", "untuk", "dengan", "dan",
    "atau", "ini", "itu", "juga", "sudah", "akan", "bisa", "ada", "apa",
    "siapa", "bagaimana", "mengapa", "kapan", "dimana", "mana", "apakah",
    "saya", "kami", "kita", "kamu", "anda", "mereka", "dia", "adalah",
    "sebagai", "oleh", "tentang", "seperti", "karena", "jika", "kalau",
    "agar", "supaya", "namun", "tetapi", "saja", "lagi", "banyak",
    "mau", "tahu", "tolong", "bantu", "kasih", "terima", "halo", "hai",
    "selamat", "pagi", "siang", "sore", "malam", "kak", "min", "admin",
}

COMMON_WORDS = {
    "informasi", "info", "tentang", "program", "kegiatan", "aksi",
    "layanan", "cara", "apa", "bagaimana", "siapa", "dimana",
}


def _tokenize(text: str) -> list[str]:
    """Tokenize Indonesian/English text into clean normalized words."""
    cleaned = re.sub(r"[^\w\s-]", " ", text.lower())
    words = re.split(r"[\s/]+", cleaned)
    tokens: list[str] = []
    for w in words:
        w = w.strip("-_")
        if len(w) > 1 and w not in STOP_WORDS:
            tokens.append(w)
    return tokens


def _expand_query(tokens: list[str]) -> list[str]:
    """Expand query tokens using domain synonyms."""
    expanded: list[str] = []
    for t in tokens:
        if t in SYNONYMS:
            for syn in SYNONYMS[t]:
                for syn_token in _tokenize(syn):
                    if syn_token not in tokens and syn_token not in expanded:
                        expanded.append(syn_token)
    return expanded


def _chunk_similarity(c1: str, c2: str) -> float:
    """Calculate Jaccard token similarity between two chunks."""
    s1 = set(_tokenize(c1))
    s2 = set(_tokenize(c2))
    if not s1 or not s2:
        return 0.0
    return len(s1 & s2) / len(s1 | s2)


class SeasoldierKBRetrieval:
    """Intelligent TF-IDF / BM25 knowledge base retrieval for Seasoldier."""

    def __init__(
        self,
        kb_path: str,
        chunk_size: int = 140,
        overlap: int = 30,
        cache_max: int = 150,
    ):
        self.kb_path = kb_path
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.cache_max = cache_max
        self.raw_text: str = ""
        self.chunks: list[str] = []
        self.section_titles: list[str] = []
        self.idf_cache: dict[str, float] = {}
        self._search_cache: dict[str, list[SearchResult]] = {}
        self._load_and_index()

    def _load_and_index(self) -> None:
        """Load knowledge base file, split into semantic chunks, and build index."""
        if not os.path.exists(self.kb_path):
            self.raw_text = ""
            self.chunks = []
            return

        with open(self.kb_path, "r", encoding="utf-8") as f:
            self.raw_text = f.read()

        self.chunks = self._split_chunks(self.raw_text, self.chunk_size, self.overlap)
        self.idf_cache = self._compute_idf()
        self._extract_section_titles()

    def _extract_section_titles(self) -> None:
        """Extract nearest header or title for each chunk."""
        self.section_titles = []
        for chunk in self.chunks:
            lines = [l.strip() for l in chunk.split("\n") if l.strip()]
            title = ""
            for line in lines:
                if re.match(r"^(#+|BAGIAN|\d+\.|\*|[A-Z\s]{4,}:)", line):
                    title = re.sub(r"^[#=\-\s*]+", "", line).strip()
                    break
            self.section_titles.append(title if title else "Informasi Seasoldier")

    def _split_chunks(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        """Split text by semantic paragraphs while respecting word boundaries."""
        # Split by explicit sections or double newlines
        paragraphs = re.split(r"\n\s*\n|={5,}|-{5,}", text)
        result: list[str] = []
        buf: list[str] = []
        wc = 0

        for p in paragraphs:
            p_clean = p.strip()
            if not p_clean:
                continue

            p_words = len([w for w in p_clean.split() if w])
            if wc + p_words <= chunk_size:
                buf.append(p_clean)
                wc += p_words
            else:
                if buf:
                    chunk = "\n\n".join(buf).strip()
                    if chunk and len(chunk.split()) > 5:
                        result.append(chunk)
                buf = [p_clean]
                wc = p_words

        if buf:
            chunk = "\n\n".join(buf).strip()
            if chunk and len(chunk.split()) > 5:
                result.append(chunk)

        return result

    def _compute_idf(self) -> dict[str, float]:
        """Pre-compute IDF for all terms in knowledge base."""
        n = len(self.chunks)
        if n == 0:
            return {}

        doc_freq: dict[str, int] = {}
        for chunk in self.chunks:
            words = set(_tokenize(chunk))
            for w in words:
                doc_freq[w] = doc_freq.get(w, 0) + 1

        idf: dict[str, float] = {}
        for word, df in doc_freq.items():
            idf[word] = math.log((n + 1) / (df + 1)) + 1.0

        return idf

    def _get_idf(self, word: str) -> float:
        """Get IDF value for a word with fallback for new words."""
        return self.idf_cache.get(word, math.log(len(self.chunks) + 1) + 1.0)

    def _score_chunk(
        self,
        chunk: str,
        q_tokens: list[str],
        expanded: list[str],
        raw_query: str,
    ) -> float:
        """Score a chunk using enhanced TF-IDF, phrase matching, and section bonuses."""
        cl = chunk.lower()
        score = 0.0

        specific_tokens = [t for t in q_tokens if t not in COMMON_WORDS]

        # Chunk must contain at least one specific token or its expanded synonym
        if specific_tokens:
            has_specific = any(t in cl for t in specific_tokens)
            has_expanded = any(t in cl for t in expanded)
            has_prefix = any(
                any(w.startswith(t) for w in cl.split())
                for t in specific_tokens if len(t) >= 4
            )

            if not has_specific and not has_expanded and not has_prefix:
                return 0.0

        # 1. Heading / Title bonus
        first_lines = " ".join(chunk.split("\n")[:2]).lower()
        for t in specific_tokens:
            if t in first_lines:
                score += 30.0
                break

        # 2. Exact multi-word phrase matching
        ql = raw_query.lower()
        q_words = [w for w in ql.split() if len(w) > 2]
        for length in range(min(len(q_words), 4), 1, -1):
            for i in range(len(q_words) - length + 1):
                phrase = " ".join(q_words[i : i + length])
                if phrase in cl:
                    score += len(phrase.split()) * 25.0

        # 3. Direct Query Tokens TF-IDF
        for t in q_tokens:
            if t in cl:
                matches = len(re.findall(re.escape(t), cl))
                tf = min(matches, 6)
                idf = self._get_idf(t)
                weight = 3.5 if t in specific_tokens else 1.0
                score += tf * idf * weight

        # 4. Synonym / Expanded terms TF-IDF (medium weight)
        for t in expanded:
            if t in cl:
                score += self._get_idf(t) * 1.2

        # 5. Term Density Bonus
        hits = sum(1 for t in specific_tokens if t in cl)
        if hits >= 2:
            score += hits * 18.0

        # 6. Environmental Domain Boosting
        if re.search(r"konservasi|mangrove|pohon|terumbu|karang|lamun|ecobrick|clean-up|gelang|relawan|soldier|junior|warungku", cl):
            score += 10.0

        return score

    def _deduplicate(self, results: list[SearchResult], threshold: float = 0.75) -> list[SearchResult]:
        """Remove overly similar results."""
        if len(results) <= 1:
            return results

        deduped: list[SearchResult] = [results[0]]
        for candidate in results[1:]:
            if not any(_chunk_similarity(candidate.chunk, kept.chunk) > threshold for kept in deduped):
                deduped.append(candidate)
        return deduped

    def search(self, question: str, top_k: int = 6) -> list[SearchResult]:
        """Search knowledge base for the most relevant chunks."""
        cache_key = f"{question.lower().strip()}:{top_k}"
        if cache_key in self._search_cache:
            return self._search_cache[cache_key]

        q_tokens = _tokenize(question)
        if not q_tokens:
            return []

        expanded = _expand_query(q_tokens)

        results: list[SearchResult] = []
        for i, chunk in enumerate(self.chunks):
            s = self._score_chunk(chunk, q_tokens, expanded, question)
            if s > 0:
                results.append(SearchResult(
                    chunk=chunk,
                    index=i,
                    score=s,
                    section_title=self.section_titles[i] if i < len(self.section_titles) else "",
                ))

        results.sort(key=lambda r: r.score, reverse=True)

        if not results:
            return []

        best_score = results[0].score
        filtered = [r for r in results if r.score >= best_score * 0.25]
        deduped = self._deduplicate(filtered)
        final = deduped[:top_k]

        # Manage search cache size
        if len(self._search_cache) >= self.cache_max:
            oldest = next(iter(self._search_cache))
            del self._search_cache[oldest]
        self._search_cache[cache_key] = final

        return final

    def clear_cache(self) -> None:
        """Clear search cache."""
        self._search_cache.clear()
