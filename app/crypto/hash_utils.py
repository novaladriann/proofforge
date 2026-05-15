import hashlib


def calculate_sha256_from_bytes(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()


def generate_fingerprint_from_text(text: str, length: int = 16) -> str:
    """
    Membuat fingerprint pendek dari public key / teks.
    Digunakan agar public chain tidak menampilkan nama dan email pemilik.
    """
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest().upper()
    short_digest = digest[:length]

    return ":".join(
        short_digest[i:i + 2]
        for i in range(0, len(short_digest), 2)
    )


def make_public_document_label(block_index: int) -> str:
    """
    Label publik agar nama file asli tidak terbuka di public chain/API.
    """
    return f"Document Proof #{block_index}"