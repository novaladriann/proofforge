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

ChainProof adalah aplikasi web berbasis blockchain sederhana untuk membuktikan integritas dan keaslian dokumen digital secara kriptografis. Setiap dokumen yang didaftarkan akan menghasilkan satu blok baru yang berisi:

- **SHA-256 document hash** sebagai sidik jari dokumen.
- **Previous hash** untuk menghubungkan blok dengan blok sebelumnya.
- **Proof of Work** dengan difficulty 4, sehingga `block_hash` harus diawali empat angka nol (`0000`).
- **Tanda tangan digital RSA-2048 dengan RSA-PSS + SHA-256** untuk membuktikan bahwa blok ditandatangani oleh pemilik private key yang sah.

Dokumen asli tidak disimpan di blockchain. Sistem hanya menyimpan metadata dan hash dokumen. Siapa pun dapat memverifikasi keaslian dokumen tanpa login dengan mengunggah file ke halaman verifikasi atau melalui REST API publik.

---

## Mekanisme Kriptografi

| Mekanisme | Kegunaan |
|---|---|
| SHA-256 | Menghasilkan hash dokumen, menghitung hash blok, mendukung Proof of Work, dan membuat fingerprint public key. |
| RSA-2048 + RSA-PSS + SHA-256 | Menandatangani `block_hash` dengan private key user dan memverifikasi signature menggunakan public key user. |
| Proof of Work berbasis SHA-256 | Mencari `nonce` sampai `block_hash` memenuhi difficulty, yaitu diawali empat angka nol. |
| Werkzeug Password Hashing | Menyimpan password user dalam bentuk hash, bukan plaintext. Verifikasi dilakukan dengan `check_password_hash`. |
| PKCS#8 Encrypted Private Key via `BestAvailableEncryption` | Menyimpan private key RSA dalam bentuk terenkripsi menggunakan password user sebagai passphrase. |

> Catatan: `BestAvailableEncryption` adalah mekanisme enkripsi private key dari library `cryptography`. Detail algoritma internalnya dipilih oleh library/backend kriptografi yang digunakan, sehingga pada proyek ini tidak dilakukan implementasi enkripsi private key secara manual.

---

## Teknologi

- **Backend:** Python 3, Flask Framework
- **Frontend:** HTML5, Bootstrap 5, JavaScript
- **Database:** MySQL
- **Library Kriptografi:** `cryptography`, `Werkzeug`
- **Library Database:** `mysql-connector-python`
- **Konfigurasi Environment:** `python-dotenv`

---

## Prasyarat

Pastikan perangkat lunak berikut sudah terinstall sebelum menjalankan aplikasi:

- Python **3.10** atau lebih baru
- MySQL Server **8.0** atau lebih baru
- `pip` sebagai Python package manager
- Git, jika ingin clone repository

---

## Instalasi dan Menjalankan Aplikasi

### 1. Clone Repository

```bash
git clone https://github.com/novaladriann/proofforge.git
cd proofforge
```

Atau ekstrak file ZIP proyek, lalu masuk ke folder `proofforge`.

---

### 2. Buat Virtual Environment

```bash
python -m venv venv
```

Aktifkan virtual environment.

**Windows — Command Prompt:**

```cmd
venv\Scripts\activate
```

**Windows — PowerShell:**

```powershell
venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

Jika berhasil, terminal akan menampilkan `(venv)` di awal baris.

---

### 3. Install Dependensi

```bash
pip install -r requirements.txt
```

Dependensi utama yang digunakan:

| Package | Fungsi |
|---|---|
| `Flask` | Framework web backend. |
| `mysql-connector-python` | Koneksi aplikasi Flask ke MySQL. |
| `python-dotenv` | Membaca konfigurasi dari file `.env`. |
| `Werkzeug` | Password hashing dan utilitas file handling. |
| `cryptography` | RSA-2048, RSA-PSS, SHA-256, dan serialisasi key. |

---

### 4. Buat Database MySQL

File skema database tersedia di:

```text
database/proofforge.sql
```

Script ini akan membuat database `db_proofforge` beserta tabel:

- `users`
- `user_keys`
- `documents`
- `blocks`

#### Opsi A — Import melalui MySQL CLI

Dari root folder proyek, jalankan:

```bash
mysql -u root -p < database/proofforge.sql
```

Masukkan password MySQL ketika diminta.

#### Opsi B — Import dari dalam MySQL CLI

Masuk ke MySQL:

```bash
mysql -u root -p
```

Lalu jalankan:

```sql
source database/proofforge.sql;
```

#### Opsi C — Import melalui phpMyAdmin

1. Buka phpMyAdmin.
2. Pilih menu **Import**.
3. Pilih file `database/proofforge.sql`.
4. Klik **Go / Kirim**.

> Catatan: jika menggunakan MySQL versi lama dan terjadi error collation, gunakan MySQL 8.0 atau sesuaikan collation pada file SQL.

---

### 5. Konfigurasi File `.env`

Buat file `.env` di root folder proyek, sejajar dengan `run.py`.

Struktur minimal:

```text
proofforge/
├── .env
├── run.py
├── requirements.txt
└── app/
```

Isi file `.env`:

```dotenv
FLASK_SECRET_KEY=isi_dengan_string_acak_panjang_minimal_32_karakter

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=password_mysql_anda
DB_NAME=db_proofforge
```

Untuk menghasilkan `FLASK_SECRET_KEY` yang aman, jalankan:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Salin hasilnya dan gunakan sebagai nilai `FLASK_SECRET_KEY`.

> Penting: file `.env` tidak boleh di-commit ke repository. Pastikan `.env` sudah tercantum di `.gitignore`.

Contoh file `.env.example` yang boleh disertakan di repository:

```dotenv
FLASK_SECRET_KEY=change_this_secret_key
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=db_proofforge
```

---

### 6. Jalankan Aplikasi

```bash
python run.py
```

Jika berhasil, terminal akan menampilkan pesan seperti:

```text
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

Buka browser dan akses:

```text
http://127.0.0.1:5000
```

> Catatan: mode debug digunakan untuk pengembangan lokal. Jangan gunakan `debug=True` untuk deployment produksi.

---

## Struktur Folder

```text
proofforge/
├── run.py                        # Entry point aplikasi Flask
├── requirements.txt              # Daftar dependensi Python
├── .env                          # Konfigurasi environment, dibuat manual
├── .gitignore                    # File yang diabaikan Git
├── database/
│   └── proofforge.sql            # Skema database MySQL
└── app/
    ├── __init__.py               # Factory pattern Flask app
    ├── config.py                 # Konfigurasi dari .env
    ├── db.py                     # Koneksi database MySQL
    ├── auth/
    │   └── routes.py             # Registrasi, login, logout user
    ├── dashboard/
    │   └── routes.py             # Halaman dashboard
    ├── documents/
    │   └── routes.py             # Upload, verifikasi, chain, tamper, restore
    ├── api/
    │   └── routes.py             # REST API publik
    ├── crypto/
    │   ├── blockchain.py         # PoW, signing, verifikasi signature, validasi chain
    │   ├── hash_utils.py         # SHA-256, fingerprint, label publik
    │   └── key_manager.py        # RSA-2048 key generation dan private key loader
    ├── templates/                # Template HTML Jinja2
    └── static/                   # CSS, JavaScript, dan asset statis
```

---

## Fitur Utama

| Fitur | Endpoint | Akses |
|---|---|---|
| Register user | `/register` | Publik |
| Login user | `/login` | Publik |
| Logout user | `/logout` | Login required |
| Dashboard | `/dashboard` | Login required |
| Register dokumen ke blockchain | `/documents/upload` | Login required |
| Lihat dokumen saya | `/documents/my-documents` | Login required |
| Verifikasi dokumen | `/documents/verify` | Publik |
| Tampilan public chain | `/documents/chain` | Publik |
| Detail proof per blok | `/documents/proof/<index>` | Publik |
| Validasi integritas chain | `/documents/chain/validate` | Publik |
| Simulasi manipulasi blok | `/documents/chain/tamper/<index>` | Login required |
| Pulihkan blok demo | `/documents/chain/restore/<index>` | Login required |
| Dokumentasi API | `/documents/api-docs` | Publik |

---

## Alur Kerja Singkat

### 1. Registrasi User

1. User mengisi nama, email, password, dan konfirmasi password.
2. Sistem menyimpan password dalam bentuk hash menggunakan Werkzeug.
3. Sistem membuat RSA-2048 key pair.
4. Public key disimpan di database.
5. Private key disimpan dalam format PKCS#8 terenkripsi menggunakan password user.

### 2. Register Dokumen ke Blockchain

1. User login dan mengunggah dokumen.
2. User memasukkan password untuk membuka private key terenkripsi.
3. Sistem membaca file sebagai bytes.
4. Sistem menghitung SHA-256 dokumen.
5. Sistem memastikan hash dokumen belum pernah terdaftar.
6. Sistem mengambil block terakhir untuk menentukan `previous_hash`.
7. Sistem menjalankan Proof of Work untuk mencari `nonce`.
8. Sistem menghasilkan `block_hash` yang memenuhi difficulty.
9. Sistem menandatangani `block_hash` menggunakan RSA-PSS.
10. Metadata dokumen dan data blok disimpan ke database.

### 3. Verifikasi Dokumen

1. User atau pihak luar mengunggah dokumen.
2. Sistem menghitung ulang SHA-256 dari file tersebut.
3. Sistem mencari hash yang cocok pada tabel `blocks`.
4. Jika ditemukan, status dokumen adalah `TERDAFTAR`.
5. Jika tidak ditemukan, status dokumen adalah `TIDAK_DITEMUKAN`.

### 4. Validasi Chain

Sistem melakukan pengecekan pada setiap blok:

- menghitung ulang `block_hash`,
- mencocokkan `previous_hash`,
- memastikan Proof of Work valid,
- memverifikasi RSA signature menggunakan public key pemilik.

Jika salah satu pengecekan gagal, chain dinyatakan `INVALID`.

---

## REST API Publik

Semua endpoint REST API dapat diakses tanpa login.

### 1. Verifikasi Dokumen

```http
POST /api/verify
Content-Type: multipart/form-data
```

Body form-data:

| Key | Type | Keterangan |
|---|---|---|
| `document` | File | File dokumen yang ingin diverifikasi. |

> Key form-data wajib bernama `document`. Jika menggunakan nama lain seperti `file` atau `berkas`, Flask tidak akan menemukan file yang dikirim.

Contoh response jika dokumen terdaftar:

```json
{
  "success": true,
  "status": "TERDAFTAR",
  "message": "Dokumen ditemukan di blockchain ProofForge.",
  "document_hash": "abc123...",
  "proof": {
    "block_index": 1,
    "document_label": "Document Proof #1",
    "document_hash": "abc123...",
    "previous_hash": "000000...",
    "block_hash": "0000abc...",
    "nonce": 12345,
    "difficulty": 4,
    "timestamp": "2026-05-17 10:00:00",
    "owner_fingerprint": "AB:CD:EF:12:34:56:78:90"
  }
}
```

Contoh response jika dokumen tidak ditemukan:

```json
{
  "success": true,
  "status": "TIDAK_DITEMUKAN",
  "message": "Hash dokumen tidak ditemukan di blockchain ProofForge.",
  "document_hash": "def456..."
}
```

---

### 2. Lihat Seluruh Chain

```http
GET /api/chain
```

Endpoint ini mengembalikan daftar blok dalam format JSON. Response tidak menampilkan nama pemilik, email pemilik, maupun nama file asli. Identitas pemilik diganti dengan `owner_fingerprint`.

---

### 3. Status Integritas Chain

```http
GET /api/chain/status
```

Endpoint ini mengembalikan status validitas chain, total blok, dan daftar blok yang invalid jika ada manipulasi.

---

## Simulasi Manipulasi

Aplikasi menyediakan fitur simulasi manipulasi untuk kebutuhan demo dan pengujian.

Alurnya:

1. User login.
2. Buka halaman **Public Chain**.
3. Klik tombol **Simulasi Manipulasi** pada salah satu blok.
4. Sistem mengubah `document_hash` blok tersebut langsung di database.
5. Saat validasi chain dijalankan, sistem akan mendeteksi:
   - `block_hash` tidak cocok,
   - RSA signature invalid,
   - chain berstatus `INVALID`.
6. User dapat menekan tombol **Pulihkan Data Demo** untuk mengembalikan blok ke kondisi awal.

---

## Troubleshooting

### Error: `ModuleNotFoundError`

Pastikan virtual environment sudah aktif dan dependensi sudah diinstall:

```bash
pip install -r requirements.txt
```

---

### Error: `Access denied for user 'root'@'localhost'`

Periksa konfigurasi database di file `.env`:

```dotenv
DB_USER=root
DB_PASSWORD=password_mysql_anda
```

Pastikan username dan password MySQL sudah benar.

---

### Error: `Unknown database 'db_proofforge'`

Jalankan ulang script SQL:

```bash
mysql -u root -p < database/proofforge.sql
```

---

### Error PowerShell: `cannot be loaded because running scripts is disabled`

Jalankan perintah berikut di PowerShell:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Lalu aktifkan virtual environment kembali:

```powershell
venv\Scripts\Activate.ps1
```

---

### Error import SQL karena collation

Jika muncul error terkait `utf8mb4_0900_ai_ci`, kemungkinan MySQL yang digunakan lebih lama dari MySQL 8.0. Gunakan MySQL 8.0 atau ubah collation pada file SQL menjadi collation yang didukung, misalnya `utf8mb4_general_ci`.


---

## Lisensi

Proyek ini dibuat untuk keperluan akademik, yaitu Proyek Akhir (UAS) Mata Kuliah Kriptografi Modern, Program Studi Informatika.
