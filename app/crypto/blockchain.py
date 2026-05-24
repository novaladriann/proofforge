import hashlib
import base64

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature


def calculate_block_hash(
    block_index: int,
    document_hash: str,
    previous_hash: str,
    timestamp: str,
    nonce: int,
    difficulty: int
) -> str:
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
    signature = private_key.sign(
        block_hash.encode("utf-8"),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    return base64.b64encode(signature).decode("utf-8")

def verify_block_signature(public_key_pem: str, block_hash: str, signature_base64: str) -> bool:
    try:
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode("utf-8")
        )

        signature = base64.b64decode(signature_base64)

        public_key.verify(
            signature,
            block_hash.encode("utf-8"),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return True

    except InvalidSignature:
        return False
    except Exception:
        return False


def normalize_timestamp(timestamp_value) -> str:
    if hasattr(timestamp_value, "strftime"):
        return timestamp_value.strftime("%Y-%m-%d %H:%M:%S")

    return str(timestamp_value)


def validate_chain_integrity(blocks):
    results = []
    expected_previous_hash = "0" * 64
    chain_valid = True

    for block in blocks:
        timestamp_str = normalize_timestamp(block["timestamp"])

        calculated_hash = calculate_block_hash(
            block_index=int(block["block_index"]),
            document_hash=block["document_hash"],
            previous_hash=block["previous_hash"],
            timestamp=timestamp_str,
            nonce=int(block["nonce"]),
            difficulty=int(block["difficulty"])
        )

        hash_match = calculated_hash == block["block_hash"]

        previous_hash_valid = block["previous_hash"] == expected_previous_hash

        pow_valid = calculated_hash.startswith(
            "0" * int(block["difficulty"])
        )

        signature_valid = verify_block_signature(
            public_key_pem=block["public_key_pem"],
            block_hash=calculated_hash,
            signature_base64=block["owner_signature"]
        )

        block_valid = hash_match and previous_hash_valid and pow_valid and signature_valid

        if not block_valid:
            chain_valid = False

        results.append({
            "block_index": block["block_index"],
            "document_hash": block["document_hash"],
            "stored_hash": block["block_hash"],
            "calculated_hash": calculated_hash,
            "previous_hash": block["previous_hash"],
            "expected_previous_hash": expected_previous_hash,
            "hash_match": hash_match,
            "previous_hash_valid": previous_hash_valid,
            "pow_valid": pow_valid,
            "signature_valid": signature_valid,
            "block_valid": block_valid,
            "owner_name": block.get("owner_name"),
            "owner_email": block.get("owner_email"),
            "owner_fingerprint": block.get("owner_fingerprint"),
            "timestamp": block["timestamp"]
        })

        expected_previous_hash = block["block_hash"]

    return {
        "chain_valid": chain_valid,
        "results": results
    }