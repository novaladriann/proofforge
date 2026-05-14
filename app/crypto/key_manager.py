from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_rsa_key_pair(password: str):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    encrypted_private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(
            password.encode("utf-8")
        )
    )

    public_key = private_key.public_key()

    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return public_key_pem.decode("utf-8"), encrypted_private_key_pem.decode("utf-8")


def load_private_key(encrypted_private_key_pem: str, password: str):
    private_key = serialization.load_pem_private_key(
        encrypted_private_key_pem.encode("utf-8"),
        password=password.encode("utf-8")
    )

    return private_key