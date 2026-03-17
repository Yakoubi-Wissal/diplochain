#!/usr/bin/env python3
"""Initialize SQLite database with minimal schema for development."""

import sqlite3
import asyncio
from core.config import settings

async def init_sqlite_db():
    """Create minimal SQLite tables for development."""
    # Extract database path from DATABASE_URL
    db_url = settings.DATABASE_URL
    if 'sqlite' in db_url:
        db_path = db_url.replace('sqlite+aiosqlite:///', '').replace('sqlite://', '')
    else:
        raise ValueError("Only SQLite databases are supported for this script")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create minimal tables needed for authentication
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS "ROLE" (
            id_role INTEGER PRIMARY KEY AUTOINCREMENT,
            label_role VARCHAR(100),
            code VARCHAR(255) NOT NULL UNIQUE,
            id_cursus INTEGER,
            description TEXT,
            permissions JSON,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            uuid_id VARCHAR(36) UNIQUE DEFAULT (lower(hex(randomblob(16))))
        );
        
        CREATE TABLE IF NOT EXISTS "institution" (
            institution_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255),
            logo_url VARCHAR(500),
            contact_email VARCHAR(255),
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS "specialite" (
            specialite_id INTEGER PRIMARY KEY AUTOINCREMENT,
            label VARCHAR(255),
            code VARCHAR(100) UNIQUE,
            description TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS "entreprise" (
            id_entreprise INTEGER PRIMARY KEY AUTOINCREMENT,
            raison_sociale VARCHAR(255),
            secteur_activite VARCHAR(255),
            contact_email VARCHAR(255),
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS "User" (
            id_user INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(255) UNIQUE,
            password VARCHAR(500),
            token VARCHAR(500),
            tokentype VARCHAR(50),
            revoked BOOLEAN DEFAULT 0,
            expired BOOLEAN DEFAULT 0,
            email VARCHAR(255) UNIQUE,
            reset_code VARCHAR(100),
            verificationtoken_expiration DATETIME,
            reset_code_expiration DATETIME,
            verification_token VARCHAR(500),
            status VARCHAR(50),
            nom VARCHAR(100),
            prenom VARCHAR(100),
            role_id INTEGER,
            statut_diplochain VARCHAR(50),
            last_login DATETIME,
            niveau_acces VARCHAR(50) DEFAULT 'GLOBAL',
            derniere_action_audit DATETIME,
            institution_id INTEGER,
            channel_session VARCHAR(255),
            permissions JSON,
            blockchain_address VARCHAR(255) UNIQUE,
            numero_etudiant VARCHAR(50),
            date_naissance_dc DATE,
            promotion VARCHAR(100),
            entreprise_id INTEGER,
            microsoft_email VARCHAR(255),
            ms_auth_validated_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            uuid_id VARCHAR(36) UNIQUE DEFAULT (lower(hex(randomblob(16)))),
            FOREIGN KEY (role_id) REFERENCES "ROLE"(id_role),
            FOREIGN KEY (institution_id) REFERENCES institution(institution_id),
            FOREIGN KEY (entreprise_id) REFERENCES entreprise(id_entreprise)
        );
        
        CREATE TABLE IF NOT EXISTS "UserRole" (
            user_id INTEGER PRIMARY KEY,
            role_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES "User"(id_user),
            FOREIGN KEY (role_id) REFERENCES "ROLE"(id_role)
        );
        
        CREATE TABLE IF NOT EXISTS etudiant (
            etudiant_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            numero_inscription VARCHAR(50),
            promotion VARCHAR(100),
            specialite_id INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES "User"(id_user),
            FOREIGN KEY (specialite_id) REFERENCES specialite(specialite_id)
        );
        
        CREATE TABLE IF NOT EXISTS etudiant_diplome (
            etudiant_id INTEGER NOT NULL,
            diplome_id INTEGER NOT NULL,
            date_obtention DATE,
            PRIMARY KEY (etudiant_id, diplome_id),
            FOREIGN KEY (etudiant_id) REFERENCES etudiant(etudiant_id)
        );
        
        CREATE TABLE IF NOT EXISTS rapport (
            rapport_id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre VARCHAR(255),
            contenu TEXT,
            date_emission DATE,
            created_by INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES "User"(id_user)
        );
        
        CREATE TABLE IF NOT EXISTS rapport_institution (
            rapport_id INTEGER PRIMARY KEY,
            institution_id INTEGER NOT NULL,
            FOREIGN KEY (rapport_id) REFERENCES rapport(rapport_id),
            FOREIGN KEY (institution_id) REFERENCES institution(institution_id)
        );
        
        CREATE TABLE IF NOT EXISTS diplomes (
            diplome_id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre VARCHAR(500),
            mention VARCHAR(255),
            date_emission DATE,
            hash_sha256 VARCHAR(64) UNIQUE,
            tx_id_fabric VARCHAR(255),
            ipfs_cid VARCHAR(100),
            statut VARCHAR(50),
            generation_mode VARCHAR(50),
            blockchain_retry_count INTEGER DEFAULT 0,
            etudiant_id INTEGER,
            institution_id INTEGER,
            specialite_id INTEGER,
            uploaded_by INTEGER,
            annee_promotion VARCHAR(10),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME,
            FOREIGN KEY (etudiant_id) REFERENCES etudiant(etudiant_id),
            FOREIGN KEY (institution_id) REFERENCES institution(institution_id),
            FOREIGN KEY (specialite_id) REFERENCES specialite(specialite_id),
            FOREIGN KEY (uploaded_by) REFERENCES "User"(id_user)
        );
        
        CREATE TABLE IF NOT EXISTS qr_code_record (
            qr_code_id INTEGER PRIMARY KEY AUTOINCREMENT,
            identifiant_opaque VARCHAR(255) UNIQUE,
            diplome_id INTEGER,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (diplome_id) REFERENCES diplomes(diplome_id)
        );
        
        CREATE TABLE IF NOT EXISTS historique_operations (
            historique_id INTEGER PRIMARY KEY AUTOINCREMENT,
            type_operation VARCHAR(50),
            ancien_hash VARCHAR(64),
            nouvel_hash VARCHAR(64),
            tx_id_fabric VARCHAR(255),
            acteur_id INTEGER,
            ip_address VARCHAR(45),
            commentaire TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (acteur_id) REFERENCES "User"(id_user)
        );
        
        CREATE TABLE IF NOT EXISTS entreprise_auth_session (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            entreprise_id INTEGER NOT NULL,
            access_token VARCHAR(1000),
            token_expiration DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (entreprise_id) REFERENCES entreprise(id_entreprise)
        );
        
        CREATE TABLE IF NOT EXISTS entreprise_validation_request (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            entreprise_id INTEGER NOT NULL,
            diplome_id INTEGER NOT NULL,
            statut VARCHAR(50),
            requested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            validated_at DATETIME,
            FOREIGN KEY (entreprise_id) REFERENCES entreprise(id_entreprise),
            FOREIGN KEY (diplome_id) REFERENCES diplomes(diplome_id)
        );
        
        CREATE TABLE IF NOT EXISTS dashboard_metrics_daily (
            metric_date DATE PRIMARY KEY,
            nb_diplomes_emis INTEGER DEFAULT 0,
            nb_diplomes_microservice INTEGER DEFAULT 0,
            nb_diplomes_upload INTEGER DEFAULT 0,
            nb_nouveaux_etudiants INTEGER DEFAULT 0,
            nb_institutions_actives INTEGER DEFAULT 0,
            nb_diplomes_confirmes INTEGER DEFAULT 0,
            nb_diplomes_pending INTEGER DEFAULT 0,
            nb_diplomes_revoques INTEGER DEFAULT 0,
            nb_verifications INTEGER DEFAULT 0,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    conn.commit()
    conn.close()
    print("✅ SQLite database initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init_sqlite_db())
