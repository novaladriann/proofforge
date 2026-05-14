from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

from app.db import get_db_connection
from app.crypto.key_manager import generate_rsa_key_pair

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not name or not email or not password or not confirm_password:
            flash("Semua field wajib diisi.", "danger")
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash("Konfirmasi password tidak cocok.", "danger")
            return redirect(url_for("auth.register"))

        password_hash = generate_password_hash(password)

        public_key_pem, encrypted_private_key_pem = generate_rsa_key_pair(password)

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id_user FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            conn.close()
            flash("Email sudah terdaftar.", "danger")
            return redirect(url_for("auth.register"))

        cursor.execute(
            """
            INSERT INTO users (name, email, password_hash)
            VALUES (%s, %s, %s)
            """,
            (name, email, password_hash)
        )

        id_user = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO user_keys (id_user, public_key_pem, encrypted_private_key_pem)
            VALUES (%s, %s, %s)
            """,
            (id_user, public_key_pem, encrypted_private_key_pem)
        )

        conn.commit()
        cursor.close()
        conn.close()

        flash("Registrasi berhasil. Silakan login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if not user:
            flash("Email tidak ditemukan.", "danger")
            return redirect(url_for("auth.login"))

        if not check_password_hash(user["password_hash"], password):
            flash("Password salah.", "danger")
            return redirect(url_for("auth.login"))

        session["user_id"] = user["id_user"]
        session["user_name"] = user["name"]
        session["user_email"] = user["email"]

        flash("Login berhasil.", "success")
        return redirect(url_for("dashboard.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Anda berhasil logout.", "success")
    return redirect(url_for("auth.login"))