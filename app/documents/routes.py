from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash

from app.db import get_db_connection
from app.crypto.hash_utils import calculate_sha256_from_bytes
from app.crypto.key_manager import load_private_key
from app.crypto.blockchain import mine_block, sign_block_hash

documents_bp = Blueprint("documents", __name__, url_prefix="/documents")


def login_required():
    return "user_id" in session


def get_next_block_data(cursor):
    """
    Mengambil data blok terakhir.
    Kalau belum ada blok, previous_hash berisi 64 angka nol.
    """

    cursor.execute(
        """
        SELECT block_index, block_hash
        FROM blocks
        ORDER BY block_index DESC
        LIMIT 1
        """
    )

    last_block = cursor.fetchone()

    if not last_block:
        return 1, "0" * 64

    next_block_index = last_block["block_index"] + 1
    previous_hash = last_block["block_hash"]

    return next_block_index, previous_hash


@documents_bp.route("/upload", methods=["GET", "POST"])
def upload_document():
    if not login_required():
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        uploaded_file = request.files.get("document")
        signing_password = request.form.get("signing_password")

        if not uploaded_file or uploaded_file.filename == "":
            flash("Silakan pilih dokumen terlebih dahulu.", "danger")
            return redirect(url_for("documents.upload_document"))

        if not signing_password:
            flash("Password diperlukan untuk membuka private key dan menandatangani blok.", "danger")
            return redirect(url_for("documents.upload_document"))

        original_filename = secure_filename(uploaded_file.filename)
        mime_type = uploaded_file.mimetype

        file_bytes = uploaded_file.read()

        if len(file_bytes) == 0:
            flash("File kosong tidak dapat didaftarkan.", "danger")
            return redirect(url_for("documents.upload_document"))

        document_hash = calculate_sha256_from_bytes(file_bytes)
        file_size = len(file_bytes)

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT u.id_user, u.password_hash, k.encrypted_private_key_pem
                FROM users u
                JOIN user_keys k ON u.id_user = k.id_user
                WHERE u.id_user = %s
                """,
                (session["user_id"],)
            )

            user_key_data = cursor.fetchone()

            if not user_key_data:
                flash("Data kunci user tidak ditemukan.", "danger")
                return redirect(url_for("documents.upload_document"))

            if not check_password_hash(user_key_data["password_hash"], signing_password):
                flash("Password salah. Private key tidak dapat dibuka.", "danger")
                return redirect(url_for("documents.upload_document"))

            try:
                private_key = load_private_key(
                    user_key_data["encrypted_private_key_pem"],
                    signing_password
                )
            except Exception:
                flash("Gagal membuka private key. Password tidak valid atau key rusak.", "danger")
                return redirect(url_for("documents.upload_document"))

            cursor.execute(
                """
                SELECT id_document
                FROM documents
                WHERE document_hash = %s
                """,
                (document_hash,)
            )
            existing_document = cursor.fetchone()

            if existing_document:
                flash("Dokumen dengan hash yang sama sudah pernah terdaftar di sistem.", "warning")
                return redirect(url_for("documents.my_documents"))

            cursor.execute(
                """
                INSERT INTO documents
                (id_user, original_filename, document_hash, file_size, mime_type)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    session["user_id"],
                    original_filename,
                    document_hash,
                    file_size,
                    mime_type
                )
            )

            id_document = cursor.lastrowid

            block_index, previous_hash = get_next_block_data(cursor)
            difficulty = 4
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            nonce, block_hash = mine_block(
                block_index=block_index,
                document_hash=document_hash,
                previous_hash=previous_hash,
                timestamp=timestamp,
                difficulty=difficulty
            )

            owner_signature = sign_block_hash(private_key, block_hash)

            cursor.execute(
                """
                INSERT INTO blocks
                (
                    block_index,
                    id_document,
                    document_hash,
                    previous_hash,
                    block_hash,
                    nonce,
                    difficulty,
                    timestamp,
                    owner_signature,
                    created_by
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    block_index,
                    id_document,
                    document_hash,
                    previous_hash,
                    block_hash,
                    nonce,
                    difficulty,
                    timestamp,
                    owner_signature,
                    session["user_id"]
                )
            )

            conn.commit()

            flash(
                f"Dokumen berhasil didaftarkan ke blockchain. Blok #{block_index} berhasil dibuat.",
                "success"
            )
            return redirect(url_for("documents.my_documents"))

        except Exception as e:
            conn.rollback()
            flash(f"Terjadi kesalahan saat membuat blok: {str(e)}", "danger")
            return redirect(url_for("documents.upload_document"))

        finally:
            cursor.close()
            conn.close()

    return render_template("upload_document.html")


@documents_bp.route("/my-documents")
def my_documents():
    if not login_required():
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT 
            d.id_document,
            d.original_filename,
            d.document_hash,
            d.file_size,
            d.mime_type,
            d.uploaded_at,
            b.block_index,
            b.block_hash,
            b.previous_hash,
            b.nonce,
            b.difficulty
        FROM documents d
        LEFT JOIN blocks b ON d.id_document = b.id_document
        WHERE d.id_user = %s
        ORDER BY d.uploaded_at DESC
        """,
        (session["user_id"],)
    )

    documents = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("my_documents.html", documents=documents)


@documents_bp.route("/chain")
def chain():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            b.*,
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

    return render_template("chain.html", blocks=blocks)