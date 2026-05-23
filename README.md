# ChainProof — Sistem Bukti Integritas Dokumen Berbasis Blockchain

> Proyek Akhir (UAS) Mata Kuliah Kriptografi Modern  
> Program Studi Informatika  
> Kelompok **ProofForge**

---

## Anggota Kelompok

| Nama | NIM |
|---|---|
| Noval Adrian | 248810018 |
| Maya Trisnawati | 2488010050 |
| Ahmad Ali Murtadlo | 2488010056 |

---

## Deskripsi Sistem

ChainProof adalah aplikasi web berbasis blockchain sederhana untuk membuktikan integritas dan keaslian dokumen digital secara kriptografis. Setiap dokumen yang didaftarkan akan menghasilkan blok baru yang berisi:

- **SHA-256** hash dokumen
- **Proof of Work** (difficulty 4 leading zeros)
- **Tanda tangan digital RSA-2048 + PSS** milik pemilik dokumen
- **Previous hash** yang menghubungkan blok ke blok sebelumnya

Siapapun dapat memverifikasi keaslian dokumen tanpa perlu login, cukup dengan mengupload file dan sistem akan membandingkan hash-nya dengan yang tersimpan di chain.

---

## Algoritma Kriptografi

| Algoritma | Kegunaan |
|---|---|
| SHA-256 | Hashing dokumen, chaining antar blok, fingerprint public key |
| RSA-2048 + PSS | Tanda tangan digital per blok, enkripsi private key |
| PBKDF2-HMAC-SHA256 | Derivasi kunci enkripsi private key (via BestAvailableEncryption) |
| AES-256-CBC | Enkripsi penyimpanan private key di database |

---

## Teknologi

- **Backend:** Python 3, Flask Framework
- **Frontend:** HTML5, Bootstrap 5, JavaScript
- **Database:** MySQL
- **Library Kriptografi:** `cryptography` (Python), `Werkzeug`

---

## Prasyarat

Pastikan perangkat lunak berikut sudah terinstall sebelum menjalankan aplikasi:

- Python **3.10** atau lebih baru
- MySQL Server **8.0** atau lebih baru
- `pip` (Python package manager)
- Git (opsional, untuk clone repository)

---

## Instalasi & Menjalankan Aplikasi

### 1. Clone Repository

```bash
git clone https://github.com/novaladriann/proofforge.git
cd proofforge
```

Atau ekstrak file ZIP yang diunduh, lalu masuk ke folder `proofforge`.

---

### 2. Buat Virtual Environment

```bash
python -m venv venv
```

Aktifkan virtual environment:

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
source venv/bin/activate
```

Setelah aktif, prompt terminal akan menampilkan `(venv)` di awal baris.

---

### 3. Install Dependensi

```bash
pip install -r requirements.txt
```

Dependensi yang akan diinstall:

| Package | Fungsi |
|---|---|
| `Flask` | Web framework backend |
| `mysql-connector-python` | Koneksi ke database MySQL |
| `python-dotenv` | Membaca file konfigurasi `.env` |
| `Werkzeug` | Hashing password, file handling |
| `cryptography` | RSA-2048, SHA-256, padding PSS |

---

### 4. Buat Database MySQL

Buka MySQL client (MySQL Workbench, phpMyAdmin, atau terminal), lalu jalankan:

```sql
source database/proofforge.sql
```

Atau buka file `database/proofforge.sql` dan jalankan seluruh isinya. Script ini akan membuat database `db_proofforge` beserta keempat tabelnya secara otomatis.

---

### 5. Konfigurasi File `.env`

Buat file `.env` di root folder proyek (sejajar dengan `run.py`):

```
proofforge/
├── .env          ← buat file ini
├── run.py
├── requirements.txt
└── app/
```

Isi file `.env` dengan konfigurasi berikut:

```dotenv
FLASK_SECRET_KEY=isi_dengan_string_acak_panjang_minimal_32_karakter

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=password_mysql_anda
DB_NAME=db_proofforge
```

Untuk menghasilkan `FLASK_SECRET_KEY` yang aman, jalankan perintah berikut di terminal:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Salin hasilnya dan gunakan sebagai nilai `FLASK_SECRET_KEY`.

> ⚠️ **Penting:** File `.env` tidak boleh di-commit ke repository. Pastikan `.env` sudah tercantum di `.gitignore`.

---

### 6. Jalankan Aplikasi

```bash
python run.py
```

Jika berhasil, terminal akan menampilkan:

```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

Buka browser dan akses **http://127.0.0.1:5000**

---

## Struktur Folder

```
proofforge/
├── run.py                        # Entry point aplikasi Flask
├── requirements.txt              # Daftar dependensi Python
├── .env                          # Konfigurasi environment (buat manual)
├── .gitignore                    # File yang diabaikan Git
├── database/
│   └── proofforge.sql            # Skema database MySQL
└── app/
    ├── __init__.py               # Factory pattern Flask app
    ├── config.py                 # Konfigurasi dari .env
    ├── db.py                     # Koneksi database MySQL
    ├── auth/
    │   └── routes.py             # Registrasi & login user
    ├── dashboard/
    │   └── routes.py             # Halaman dashboard
    ├── documents/
    │   └── routes.py             # Upload, verifikasi, chain, tamper
    ├── api/
    │   └── routes.py             # REST API publik
    ├── crypto/
    │   ├── blockchain.py         # PoW, signing, validasi chain
    │   ├── hash_utils.py         # SHA-256, fingerprint
    │   └── key_manager.py        # RSA-2048 keygen & loader
    ├── templates/                # HTML Jinja2 templates
    └── static/                   # CSS, JavaScript, assets
```

---

## Fitur Utama

| Fitur | Endpoint | Akses |
|---|---|---|
| Register & Login | `/register`, `/login` | Publik |
| Register Dokumen ke Blockchain | `/documents/upload` | Login required |
| Lihat Dokumen Saya | `/documents/my-documents` | Login required |
| Verifikasi Dokumen | `/documents/verify` | Publik |
| Tampilan Public Chain | `/documents/chain` | Publik |
| Detail Proof per Blok | `/documents/proof/<index>` | Publik |
| Validasi Integritas Chain | `/documents/chain/validate` | Publik |
| Simulasi Manipulasi Blok | `/documents/chain/tamper/<index>` | Login required |
| Dokumentasi API | `/documents/api-docs` | Publik |

---

## REST API Publik

Semua endpoint API dapat diakses tanpa login.

### Verifikasi Dokumen

```
POST /api/verify
Content-Type: multipart/form-data
Body: document = <file>
```

**Response sukses (TERDAFTAR):**
```json
{
  "success": true,
  "status": "TERDAFTAR",
  "document_hash": "abc123...",
  "proof": {
    "block_index": 1,
    "block_hash": "0000abc...",
    "timestamp": "2026-05-17 10:00:00",
    "owner_fingerprint": "AB:CD:EF:12:34:56:78:90"
  }
}
```

### Lihat Seluruh Chain

```
GET /api/chain
```

### Status Integritas Chain

```
GET /api/chain/status
```

---

## Troubleshooting

**Error: `ModuleNotFoundError`**
Pastikan virtual environment sudah aktif dan dependensi sudah diinstall:
```bash
pip install -r requirements.txt
```

**Error: `Access denied for user 'root'@'localhost'`**
Periksa konfigurasi `DB_USER` dan `DB_PASSWORD` di file `.env`.

**Error: `Unknown database 'db_proofforge'`**
Jalankan ulang script SQL:
```bash
mysql -u root -p < database/proofforge.sql
```

**Error PowerShell: `cannot be loaded because running scripts is disabled`**
Jalankan perintah ini terlebih dahulu:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Lisensi

Proyek ini dibuat untuk keperluan akademik — Proyek Akhir (UAS) Mata Kuliah Kriptografi Modern, Program Studi Informatika.
