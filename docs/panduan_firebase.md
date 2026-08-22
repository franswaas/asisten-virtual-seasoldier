# Panduan Migrasi & Deployment ke Firebase 🔥🌊
> **Asisten Virtual Seasoldier Indonesia — Firebase Hosting & Cloud Backend**

Panduan ini berisi instruksi lengkap mengenai arsitektur, konfigurasi, dan deployment antarmuka (frontend) serta serverless backend Asisten Virtual Seasoldier ke Google Firebase.

---

## 🎯 Ringkasan Arsitektur & Live Deployment

Sistem telah dikonfigurasi dan dipublikasikan pada:
- **Firebase Project ID**: `asisten-seasoldier`
- **Live URL Firebase Hosting**: **[https://asisten-seasoldier.web.app/](https://asisten-seasoldier.web.app/)**
- **Domain Cadangan**: `https://asisten-seasoldier.firebaseapp.com/`

Sistem mendukung 2 mode operasional:
1. **Mode Serverless Cloud (Firebase Cloud Functions / Render.com)**:
   - Frontend di Firebase Hosting global CDN.
   - Backend berjalan 24/7 di cloud tanpa perlu laptop atau tunnel aktif.
2. **Mode Hybrid (Tunnel / Laptop Server)**:
   - Frontend di Firebase Hosting, backend berjalan di laptop via `start_public_server.bat` (FastAPI + Cloudflare Tunnel).

---

## 📂 File Konfigurasi Firebase

- **`firebase.json`**: Mengarahkan publik hosting ke folder `frontend/`, cache control aset statis, dan URL rewrite.
- **`.firebaserc`**: Menentukan target default project (`asisten-seasoldier`).
- **`functions/`**: Berisi source code Python FastAPI serverless untuk Firebase Cloud Functions.
- **`deploy_firebase.bat`**: Skrip Windows 1-klik untuk deploy hosting atau ganti project.

---

## 🚀 Panduan Deployment Frontend (Firebase Hosting)

Jika ada perubahan tampilan, gaya CSS, atau logika JavaScript di folder `frontend/`:
1. Klik dua kali file **`deploy_firebase.bat`**.
2. Pilih nomor **`2`** (Deploy Frontend Saja).
3. Firebase CLI akan mengunggah file yang diperbarui ke CDN global dalam hitungan detik.

Atau jalankan via terminal:
```bash
firebase deploy --only hosting
```

---

## 🔌 Panduan Menghubungkan Backend

### Opsi A: Jalankan Backend Laptop via Tunnel
1. Jalankan **`start_public_server.bat`** di laptop.
2. Terminal akan menampilkan **Public HTTPS URL** (contoh: `https://xxxx.trycloudflare.com`).
3. Buka **[https://asisten-seasoldier.web.app/](https://asisten-seasoldier.web.app/)**.
4. Klik tombol **Pengaturan (⚙️)** di pojok kanan atas.
5. Masukkan Public HTTPS URL tersebut, klik **Uji Koneksi**, lalu **Simpan & Terapkan**.

### Opsi B: Deploy Backend Permanen ke Cloud (Render / Cloud Functions)
- **Render.com (100% Gratis)**: Sambungkan repo GitHub ke Render Web Service, jalankan `uvicorn main:app --host 0.0.0.0 --port $PORT`, lalu pasang URL Render sebagai default di `frontend/app.js`.
- **Firebase Cloud Functions**: Tingkatkan project ke paket Blaze di Firebase Console, lalu jalankan `firebase deploy`.

---

## 🛡️ Aturan Identitas & Kata Terlarang (Strict Rule)
- Dilarang keras menggunakan kata: **`"yayasan"`**, **`"ai bot"`**, atau **`"bot"`**.
- Selalu sebut organisasi sebagai: **Seasoldier**, **Seasoldier Indonesia**, atau **gerakan Seasoldier**.
- Selalu sebut asisten sebagai: **Asisten Virtual Seasoldier**.
