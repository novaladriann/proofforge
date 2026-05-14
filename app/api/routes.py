from flask import Blueprint, request, jsonify

from app.db import get_db_connection
from app.crypto.hash_utils import calculate_sha256_from_bytes
from app.crypto.blockchain import validate_chain_integrity

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/verify", methods=["POST"])
def api_verify_document():
    uploaded_file = request.files.get("document")

    if not uploaded_file or uploaded_file.filename == "":
        return jsonify({
            "success": False,
            "message": "File dokumen wajib dikirim dengan field name 'document'."
        }), 400

    file_bytes = uploaded_file.read()

    if len(file_bytes) == 0:
        return jsonify({
            "success": False,
            "message": "File kosong tidak dapat diverifikasi."
        }), 400

    document_hash = calculate_sha256_from_bytes(file_bytes)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            b.block_index,
            b.document_hash,
            b.previous_hash,
            b.block_hash,
            b.nonce,
            b.difficulty,
            b.timestamp,
            d.original_filename,
            d.file_size,
            d.mime_type,
            d.uploaded_at,
            u.name AS owner_name,
            u.email AS owner_email
        FROM blocks b
        LEFT JOIN documents d ON b.id_document = d.id_document
        JOIN users u ON b.created_by = u.id_user
        WHERE b.document_hash = %s
        LIMIT 1
        """,
        (document_hash,)
    )

    block = cursor.fetchone()

    cursor.close()
    conn.close()

    if not block:
        return jsonify({
            "success": True,
            "status": "TIDAK_DITEMUKAN",
            "message": "Hash dokumen tidak ditemukan di blockchain ProofForge.",
            "document_hash": document_hash
        }), 200

    return jsonify({
        "success": True,
        "status": "TERDAFTAR",
        "message": "Dokumen ditemukan di blockchain ProofForge.",
        "document_hash": document_hash,
        "proof": {
            "block_index": block["block_index"],
            "document_hash": block["document_hash"],
            "previous_hash": block["previous_hash"],
            "block_hash": block["block_hash"],
            "nonce": block["nonce"],
            "difficulty": block["difficulty"],
            "timestamp": str(block["timestamp"]),
            "owner_name": block["owner_name"],
            "owner_email": block["owner_email"],
            "original_filename": block["original_filename"],
            "file_size": block["file_size"],
            "mime_type": block["mime_type"],
            "uploaded_at": str(block["uploaded_at"])
        }
    }), 200


@api_bp.route("/chain", methods=["GET"])
def api_get_chain():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            b.block_index,
            b.document_hash,
            b.previous_hash,
            b.block_hash,
            b.nonce,
            b.difficulty,
            b.timestamp,
            d.original_filename,
            u.name AS owner_name,
            u.email AS owner_email
        FROM blocks b
        LEFT JOIN documents d ON b.id_document = d.id_document
        JOIN users u ON b.created_by = u.id_user
        ORDER BY b.block_index ASC
        """
    )

    blocks = cursor.fetchall()

    cursor.close()
    conn.close()

    chain_data = []

    for block in blocks:
        chain_data.append({
            "block_index": block["block_index"],
            "document_hash": block["document_hash"],
            "previous_hash": block["previous_hash"],
            "block_hash": block["block_hash"],
            "nonce": block["nonce"],
            "difficulty": block["difficulty"],
            "timestamp": str(block["timestamp"]),
            "original_filename": block["original_filename"],
            "owner_name": block["owner_name"],
            "owner_email": block["owner_email"]
        })

    return jsonify({
        "success": True,
        "total_blocks": len(chain_data),
        "chain": chain_data
    }), 200


@api_bp.route("/chain/status", methods=["GET"])
def api_chain_status():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            b.*,
            u.name AS owner_name,
            u.email AS owner_email,
            k.public_key_pem
        FROM blocks b
        JOIN users u ON b.created_by = u.id_user
        JOIN user_keys k ON u.id_user = k.id_user
        ORDER BY b.block_index ASC
        """
    )

    blocks = cursor.fetchall()

    cursor.close()
    conn.close()

    validation = validate_chain_integrity(blocks)

    invalid_blocks = []

    for item in validation["results"]:
        if not item["block_valid"]:
            invalid_blocks.append({
                "block_index": item["block_index"],
                "hash_match": item["hash_match"],
                "previous_hash_valid": item["previous_hash_valid"],
                "pow_valid": item["pow_valid"],
                "signature_valid": item["signature_valid"]
            })

    return jsonify({
        "success": True,
        "chain_valid": validation["chain_valid"],
        "total_blocks": len(validation["results"]),
        "invalid_blocks": invalid_blocks
    }), 200