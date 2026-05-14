import hashlib
import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes


def calculate_block_hash(
    block_index: int,
    document_hash: str,
    previous_hash: str,
    timestamp: str,
    nonce: int,
    difficulty: int
) -> str:
    """
    Membuat hash SHA-256 untuk sebuah blok.
    Data dibuat dalam format konsisten agar hasil hash selalu sama.
    """

    block_data = (
        f"{block_index}|"
        f"{document_hash}|"
        f"{previous_hash}|"
        f"{timestamp}|"
        f"{nonce}|"
        f"{difficulty}"
    )

    return hashlib.sha256(block_data.encode("utf-8")).hexdigest()


def mine_block(
    block_index: int,
    document_hash: str,
    previous_hash: str,
    timestamp: str,
    difficulty: int = 4
):
    """
    Proof of Work sederhana.
    Sistem mencari nonce sampai block_hash diawali sejumlah nol sesuai difficulty.
    Contoh difficulty 4 berarti hash harus diawali '0000'.
    """

    nonce = 0
    target_prefix = "0" * difficulty

    while True:
        block_hash = calculate_block_hash(
            block_index=block_index,
            document_hash=document_hash,
            previous_hash=previous_hash,
            timestamp=timestamp,
            nonce=nonce,
            difficulty=difficulty
        )

        if block_hash.startswith(target_prefix):
            return nonce, block_hash

        nonce += 1


def sign_block_hash(private_key, block_hash: str) -> str:
    """
    Menandatangani block_hash menggunakan private key RSA milik user.
    Signature disimpan dalam format base64 agar aman dimasukkan ke database.
    """

    signature = private_key.sign(
        block_hash.encode("utf-8"),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    return base64.b64encode(signature).decode("utf-8")