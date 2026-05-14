CREATE DATABASE IF NOT EXISTS db_proofforge;
USE db_proofforge;

CREATE TABLE users (
    id_user INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_keys (
    id_key INT AUTO_INCREMENT PRIMARY KEY,
    id_user INT NOT NULL,
    public_key_pem TEXT NOT NULL,
    encrypted_private_key_pem TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_user) REFERENCES users(id_user)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE documents (
    id_document INT AUTO_INCREMENT PRIMARY KEY,
    id_user INT NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    document_hash CHAR(64) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_user) REFERENCES users(id_user)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE blocks (
    id_block INT AUTO_INCREMENT PRIMARY KEY,
    block_index INT NOT NULL UNIQUE,
    id_document INT,
    document_hash CHAR(64) NOT NULL,
    previous_hash CHAR(64) NOT NULL,
    block_hash CHAR(64) NOT NULL,
    nonce INT NOT NULL,
    difficulty INT NOT NULL DEFAULT 4,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    owner_signature TEXT NOT NULL,
    created_by INT NOT NULL,

    FOREIGN KEY (id_document) REFERENCES documents(id_document)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    FOREIGN KEY (created_by) REFERENCES users(id_user)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);