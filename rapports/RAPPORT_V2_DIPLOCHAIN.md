# 📋 RAPPORT TECHNIQUE COMPLET — DiploChain Backend v2

> **Date de génération** : 2026-03-17  
> **Environnement de test** : SQLite en mémoire (mode standalone, sans Docker)  
> **Auteur de l'analyse** : Agent IA — FastAPI & Microservices Expert

---

## 🏗️ ARCHITECTURE GLOBALE

### Schéma des microservices

```
                        ┌──────────────────────┐
                        │     API Gateway       │
                        │    Port Docker: 8000  │
                        │  Route: /api/{service}│
                        └──────────┬───────────┘
                                   │ Proxying HTTP
              ┌────────────────────┼────────────────────────────┐
              │                    │                            │
    ┌─────────▼──────┐  ┌──────────▼───────┐  ┌───────────────▼──────┐
    │  user-service  │  │institution-service│  │   student-service    │
    │  /users/*      │  │  /institutions/*  │  │    /students/*       │
    └────────────────┘  └──────────────────┘  └──────────────────────┘
    ┌────────────────┐  ┌──────────────────┐  ┌──────────────────────┐
    │diploma-service │  │blockchain-service │  │   storage-service    │
    │  /diplomas/*   │  │  /blockchain/*   │  │    /storage/*        │
    └────────────────┘  └──────────────────┘  └──────────────────────┘
    ┌────────────────┐  ┌──────────────────┐  ┌──────────────────────┐
    │document-service│  │ entreprise-service│  │ notification-service │
    │  /rapports/*   │  │  /entreprises/*  │  │  /notifications/*    │
    └────────────────┘  └──────────────────┘  └──────────────────────┘
    ┌────────────────┐  ┌──────────────────┐  ┌──────────────────────┐
    │analytics-service│ │admin-dashboard-  │  │ verification-service │
    │  /analytics/*  │  │service /admin/*  │  │    /verify/*         │
    └────────────────┘  └──────────────────┘  └──────────────────────┘
    ┌────────────────┐  ┌──────────────────┐  ┌──────────────────────┐
    │pdf-generator-  │  │qr-validation-    │  │  retry-worker-       │
    │service /pdf/*  │  │service /qr/*     │  │  service (worker)    │
    └────────────────┘  └──────────────────┘  └──────────────────────┘
```

### Infrastructure (docker-compose.v2.yml)
| Composant           | Image                        | Port  | Rôle                      |
|---------------------|------------------------------|-------|---------------------------|
| PostgreSQL          | postgres:14.2                | 5432  | Base de données principale|
| IPFS Node           | ipfs/kubo:latest             | 5001/8080 | Stockage fichiers décentralisé |
| Hyperledger Fabric  | hyperledger/fabric-peer:latest | 7051 | Blockchain Fabric         |
| API Gateway         | ./api-gateway                | 8000  | Point d'entrée unique     |
| 13 microservices    | ./*/                         | interne| Services métier          |

---

## 🔌 API GATEWAY

**Fichier** : `api-gateway/app/main.py`  
**Port Docker** : 8000  
**Rôle** : Proxy inverse unique — route toutes les requêtes vers les microservices  

### Route unique de proxy

| Méthode | Route | Description |
|---------|-------|-------------|
| GET/POST/PUT/DELETE/PATCH | `/api/{service}/{path:path}` | Proxy vers le microservice correspondant |
| GET | `/health` | Santé de la gateway |

### Table de routage (SERVICE_MAP)

| Clé URL         | Service cible                             |
|-----------------|-------------------------------------------|
| `users`         | `http://user-service:8000`               |
| `institutions`  | `http://institution-service:8000`        |
| `students`      | `http://student-service:8000`            |
| `diplomas`      | `http://diploma-service:8000`            |
| `documents`     | `http://document-service:8000`           |
| `blockchain`    | `http://blockchain-service:8000`         |
| `storage`       | `http://storage-service:8000`            |
| `verify`        | `http://verification-service:8000`       |
| `analytics`     | `http://analytics-service:8000`          |
| `entreprises`   | `http://entreprise-service:8000`         |
| `notifications` | `http://notification-service:8000`       |
| `pdf`           | `http://pdf-generator-service:8000`      |
| `admin`         | `http://admin-dashboard-service:8000`    |
| `qr`            | `http://qr-validation-service:8000`      |

### Exemple d'appel via Gateway

```http
# Via Gateway (production)
GET /api/users/1
→ proxy → http://user-service:8000/users/1

POST /api/diplomas/
→ proxy → http://diploma-service:8000/diplomas/
```

### ⚠️ BUG CRITIQUE #1 — URL de proxy malformée

```python
# Code actuel (bugué)
url = f"{base}/{service}/{url_path}"
# Résultat: http://user-service:8000/users/users/1  ← DOUBLE segment!

# Correction suggérée:
url = f"{base}/{url_path}"
```

---

## 👤 1. USER-SERVICE

**Fichier principal** : `user-service/app/main.py`  
**Port local test** : 8001  
**Base de données** : Table `User`, `ROLE`, `UserRole`  
**Status test** : ✅ **FONCTIONNEL**

### Modèles de données

#### Table `User`
| Champ | Type | Contrainte | Description |
|-------|------|-----------|-------------|
| `id_user` | Integer | PK, auto | Identifiant unique |
| `username` | String(255) | - | Nom d'utilisateur |
| `password` | String(120) | - | Mot de passe hashé (bcrypt) |
| `email` | String(255) | UNIQUE | Email (identifiant login) |
| `token` | String(255) | - | Token JWT courant |
| `tokentype` | String(50) | - | Type de token |
| `revoked` | Boolean | - | Token révoqué |
| `expired` | Boolean | - | Token expiré |
| `reset_code` | String(255) | - | Code de réinitialisation |
| `verification_token` | String(255) | UNIQUE | Token de vérification email |
| `verificationtoken_expiration` | DateTime | - | Expiration vérification |
| `reset_code_expiration` | DateTime | - | Expiration reset |
| `status` | String(255) | - | Statut: ACTIVE, VERIFIED, BLOCKED |

#### Table `ROLE`
| Champ | Type | Contrainte | Description |
|-------|------|-----------|-------------|
| `id_role` | Integer | PK, auto | Identifiant |
| `code` | String(255) | UNIQUE | Code: SUPER_ADMIN, INSTITUTION_ADMIN... |
| `label_role` | String(100) | - | Libellé |
| `id_cursus` | Integer | - | Cursus associé (optionnel) |

#### Table `UserRole` (pivot)
| Champ | Type | Description |
|-------|------|-------------|
| `user_id` | FK(User) | Référence utilisateur |
| `role_id` | FK(ROLE) | Référence rôle |

### Endpoints

#### 🔐 Authentification (`/users/auth`)

| Méthode | Route | Description | Auth requis |
|---------|-------|-------------|-------------|
| POST | `/users/auth/login` | Connexion, retourne JWT | Non |
| GET | `/users/auth/me` | Profil utilisateur courant | ✅ Bearer JWT |

**POST /users/auth/login**
```json
// Request (form-data x-www-form-urlencoded)
username=admin@diplochain.tn&password=Admin@1234

// Response 200
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}

// Errors
401 Unauthorized: { "detail": "Email ou mot de passe incorrect" }
```

**GET /users/auth/me**
```json
// Headers: Authorization: Bearer <token>

// Response 200
{
  "id_user": 1,
  "username": "admin",
  "email": "admin@diplochain.tn",
  "status": "ACTIVE",
  "revoked": false,
  "expired": false,
  "token": null,
  "tokentype": null,
  "reset_code": null,
  "verification_token": null,
  "verificationtoken_expiration": null,
  "reset_code_expiration": null
}

// Errors
401 Unauthorized: { "detail": "Token invalide ou expiré" }
```

#### 👥 Gestion Utilisateurs (`/users`)

| Méthode | Route | Description | Auth requis |
|---------|-------|-------------|-------------|
| GET | `/users/` | Health check (⚠️ voir bug #2) | Non |
| POST | `/users/` | Créer utilisateur | Non |
| GET | `/users/{user_id}` | Lire utilisateur par ID | Non |
| PUT | `/users/{user_id}` | Modifier utilisateur | Non |

**POST /users/**
```json
// Request
{
  "email": "user@diplochain.tn",
  "username": "user1",
  "password": "MonMotDePasse123",
  "status": "ACTIVE",
  "revoked": false,
  "expired": false
}

// Response 201
{
  "id_user": 1,
  "username": "user1",
  "email": "user@diplochain.tn",
  "status": "ACTIVE",
  "revoked": false,
  "expired": false,
  "token": null,
  "tokentype": null,
  "reset_code": null,
  "verification_token": null,
  "verificationtoken_expiration": null,
  "reset_code_expiration": null
}

// Errors
422: Validation error (email invalide, etc.)
```

**GET /users/{user_id}**
```json
// Response 200 (même structure que ci-dessus)
// Error: 404 { "detail": "User not found" }
```

**PUT /users/{user_id}**
```json
// Request (tous les champs optionnels)
{
  "username": "nouveau_username",
  "email": "nouveau@email.tn",
  "status": "VERIFIED"
}

// Response 200 (objet UserRead)
// Error: 404 { "detail": "User not found" }
```

#### 🎭 Gestion Rôles (`/users/roles`)

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/users/roles/` | Lister tous les rôles |
| POST | `/users/roles/` | Créer un rôle |
| GET | `/users/roles/{id_role}` | Lire un rôle |
| PUT | `/users/roles/{id_role}` | Modifier un rôle |

**POST /users/roles/**
```json
// Request
{
  "code": "SUPER_ADMIN",
  "label_role": "Super Administrateur",
  "id_cursus": null
}

// Response 200
{
  "id_role": 1,
  "code": "SUPER_ADMIN",
  "label_role": "Super Administrateur",
  "id_cursus": null
}
```

**GET /users/roles/**
```json
// Query params: ?code=SUPER_ADMIN (optionnel)
// Response 200
[
  { "id_role": 1, "code": "SUPER_ADMIN", "label_role": "Super Administrateur", "id_cursus": null }
]
```

### ⚠️ BUGS USER-SERVICE

| # | Sévérité | Description | Localisation |
|---|---------|-------------|-------------|
| B1 | 🔴 CRITIQUE | **Double déclaration `tokentype`** dans le modèle `User` (ligne 31 et 33) | `models.py:31,33` |
| B2 | 🟡 MOYEN | **Conflit de route** : `GET /users/` retourne health check (masque `list_users`) | `users.py:12,40` |
| B3 | 🟡 MOYEN | **Aucune protection** sur `POST /users/` — tout le monde peut créer un compte | `users.py:23` |
| B4 | 🟡 MOYEN | **Aucune protection** sur `PUT /users/{id}` — pas d'authent | `users.py:50` |
| B5 | 🟢 FAIBLE | `password` non hashé dans `PUT /users/` | `users.py:50` |

**Correction B1** (double tokentype dans models.py) :
```python
# SUPPRIMER la ligne 33 dupliquée
tokentype = Column(String(50))  # ligne 31 → garder
# tokentype = Column(String(50))  ← ligne 33 à supprimer
```

**Correction B2** (route conflit) :
```python
# Changer le health check vers /users/health
@router.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
```

---

## 🎓 2. DIPLOMA-SERVICE

**Fichier principal** : `diploma-service/app/main.py`  
**Port local test** : 8002  
**Status test** : ❌ **ERREUR CRITIQUE (UUID + SQLite)**

### Modèles de données

#### Table `diplomes`
| Champ | Type | Contrainte | Description |
|-------|------|-----------|-------------|
| `id` | UUID | PK | Identifiant unique (UUID v4) |
| `titre` | String(255) | NOT NULL | Titre du diplôme |
| `mention` | String(100) | - | Mention obtenue |
| `date_emission` | Date | NOT NULL | Date d'émission |
| `hash_sha256` | String(64) | NOT NULL | Hash du PDF |
| `tx_id_fabric` | String(255) | - | Transaction ID Hyperledger |
| `ipfs_cid` | String(255) | NOT NULL | CID IPFS du PDF |
| `statut` | String(50) | DEFAULT 'ORIGINAL' | ORIGINAL, CONFIRME, REVOQUE |
| `etudiant_id` | UUID | NOT NULL | Référence étudiant |
| `institution_id` | UUID | NOT NULL | Référence institution |
| `specialite_id` | UUID | - | Référence spécialité |
| `template_id` | UUID | - | Référence template PDF |
| `uploaded_by` | UUID | NOT NULL | Utilisateur créateur |
| `created_at` | Date | DEFAULT now() | Date de création |
| `updated_at` | Date | - | Date de modification |

#### Table `diploma_status_history`
| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | PK |
| `diploma_id` | UUID FK | Référence diplôme |
| `old_status` | String(50) | Ancien statut |
| `new_status` | String(50) | Nouveau statut |
| `changed_at` | Date | Date de changement |

### Endpoints

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/diplomas/health` | Santé du service |
| POST | `/diplomas/` | Créer un diplôme |
| GET | `/diplomas/{diploma_id}` | Lire un diplôme (UUID) |
| PUT | `/diplomas/{diploma_id}` | Modifier un diplôme |
| POST | `/diplomas/{diploma_id}/revoke` | Révoquer un diplôme |

**POST /diplomas/**
```json
// Request
{
  "titre": "Master en Informatique",
  "mention": "Très Bien",
  "date_emission": "2024-06-15",
  "hash_sha256": "abc123def456abc123def456abc123def456abc123def456abc123def456abc1",
  "ipfs_cid": "QmTestCID123456789",
  "statut": "ORIGINAL",
  "etudiant_id": "550e8400-e29b-41d4-a716-446655440000",
  "institution_id": "550e8400-e29b-41d4-a716-446655440001",
  "specialite_id": null,
  "template_id": null,
  "uploaded_by": "550e8400-e29b-41d4-a716-446655440002"
}

// Response 200 (+ id UUID généré automatiquement)
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "titre": "Master en Informatique",
  "mention": "Très Bien",
  "date_emission": "2024-06-15",
  ...
  "created_at": "2024-06-15",
  "updated_at": null
}
```

**POST /diplomas/{id}/revoke**
```json
// Response 200 — statut devient "REVOQUE" + entrée dans diploma_status_history
{
  "id": "a1b2c3d4-...",
  "statut": "REVOQUE",
  ...
}
```

### ⚠️ BUGS DIPLOMA-SERVICE

| # | Sévérité | Description | Correction |
|---|---------|-------------|-----------|
| B1 | 🔴 CRITIQUE | **main.py incomplet** — manque corps de `on_startup` | ✅ Corrigé |
| B2 | 🔴 CRITIQUE | **`postgresql.UUID` incompatible SQLite** — crash sur `db.commit()` | Utiliser `String(36)` pour SQLite ou forcer PostgreSQL |
| B3 | 🟡 MOYEN | **Pas de liste des diplômes** — aucun endpoint `GET /diplomas/` | Ajouter endpoint liste |
| B4 | 🟡 MOYEN | **Hash SHA256 non validé** — longueur non vérifiée (devrait être 64 chars) | Ajouter validator |
| B5 | 🟢 FAIBLE | **Aucune authentification** sur les endpoints | Ajouter `Depends(get_current_user)` |

**Correction B2** (UUID PostgreSQL vs SQLite) :
```python
# Option 1 : Utiliser String pour la compatibilité
from sqlalchemy import Column, String
import uuid

class Diploma(Base):
    __tablename__ = "diplomes"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    etudiant_id = Column(String(36), nullable=False)
    # ... etc.

# Option 2 (recommandée en production) : 
# Ne jamais tester avec SQLite — utiliser uniquement PostgreSQL
```

---

## 🏫 3. INSTITUTION-SERVICE

**Fichier principal** : `institution-service/app/main.py`  
**Port local test** : 8003  
**Status test** : ✅ **FONCTIONNEL**

### Modèles de données

#### Table `institution`
| Champ | Type | Description |
|-------|------|-------------|
| `institution_id` | Integer PK | Identifiant |
| `nom_institution` | String(255) | Nom |
| `adresse` | String(255) | Adresse physique |
| `code_postal` | String(20) | Code postal |
| `ville` | String(100) | Ville |
| `date_creation` | Date | Date de création |
| `pays` | String(100) | Pays |
| `telephone` | String(20) | Téléphone |
| `email_institution` | String(100) | Email officiel |
| `site_web` | String(255) | Site web |
| `chiffre_affaires` | Numeric(15,2) | Chiffre d'affaires |
| `nombre_employes` | Integer | Effectif |
| `description` | String(255) | Description |
| `id_group_institution` | Integer | Groupe parent |
| `date_mise_a_jour` | DateTime | Dernière mise à jour |

#### Table `institution_blockchain_ext`
| Champ | Type | Description |
|-------|------|-------------|
| `institution_id` | Integer PK | Référence institution |
| `channel_id` | String(100) | Canal Fabric UNIQUE |
| `peer_node_url` | String(255) | URL nœud Fabric |
| `status` | String(50) | Statut blockchain |
| `code` | String(20) | Code interne |
| `created_at` | DateTime | Date création |

### Endpoints

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/institutions/health` | Santé |
| POST | `/institutions/` | Créer institution |
| GET | `/institutions/` | Lister institutions (filtre `?active=true/false`) |
| GET | `/institutions/{id}` | Lire institution |
| PUT | `/institutions/{id}` | Modifier institution |
| POST | `/institutions/{id}/blockchain` | Ajouter config blockchain |
| GET | `/institutions/{id}/students` | Lister étudiants (proxy → student-service) |

**POST /institutions/**
```json
// Request
{
  "nom_institution": "Esprit School of Engineering",
  "adresse": "2 Rue de la Paix",
  "code_postal": "2080",
  "ville": "Ariana",
  "date_creation": "2002-01-01",
  "pays": "Tunisie",
  "telephone": "+216 71 123 456",
  "email_institution": "contact@esprit.tn",
  "site_web": "https://esprit.tn",
  "nombre_employes": 500
}

// Response 200
{
  "institution_id": 1,
  "nom_institution": "Esprit School of Engineering",
  "adresse": "2 Rue de la Paix",
  "code_postal": "2080",
  "ville": "Ariana",
  "date_creation": "2002-01-01",
  "pays": "Tunisie",
  "telephone": "+216 71 123 456",
  "email_institution": "contact@esprit.tn",
  "site_web": "https://esprit.tn",
  "chiffre_affaires": null,
  "nombre_employes": 500,
  "description": null,
  "id_group_institution": null,
  "date_mise_a_jour": "2026-03-17T08:57:05"
}
```

**POST /institutions/{id}/blockchain**
```json
// Request
{
  "channel_id": "channel-esprit",
  "peer_node_url": "grpc://peer0.esprit.diplochain.tn:7051",
  "status": "ACTIVE",
  "code": "ESPRIT01"
}

// Response 200
{
  "institution_id": 1,
  "channel_id": "channel-esprit",
  "peer_node_url": "grpc://peer0.esprit.diplochain.tn:7051",
  "status": "ACTIVE",
  "code": "ESPRIT01",
  "created_at": "2026-03-17T09:00:00"
}
```

### ⚠️ BUGS INSTITUTION-SERVICE

| # | Sévérité | Description | Correction |
|---|---------|-------------|-----------|
| B1 | 🟡 MOYEN | **`PUT /institutions/{id}` utilise `InstitutionRead` au lieu de `InstitutionUpdate`** — impose tous les champs | Créer `InstitutionUpdate` avec champs optionnels |
| B2 | 🟡 MOYEN | **Proxy `GET /institutions/{id}/students`** — timeout 5s trop court, aucune gestion d'erreur | Améliorer gestion erreurs |
| B3 | 🟢 FAIBLE | **Filtre `?active=true/false`** — ne supporte pas le filtre `ARCHIVEE` correctement | Implémenter filtre par `status` directement |

---

## 👨‍🎓 4. STUDENT-SERVICE

**Fichier principal** : `student-service/app/main.py`  
**Port local test** : 8004  
**Status test** : ✅ **PARTIELLEMENT FONCTIONNEL** (problème route GET /)

### Modèle de données

#### Table `etudiant`
| Champ | Type | Description |
|-------|------|-------------|
| `etudiant_id` | String(10) PK | ID alphanumérique (ex: STU001) |
| `email_etudiant` | String(100) | Email personnel |
| `nom` | String(100) | Nom de famille |
| `prenom` | String(100) | Prénom |
| `date_naissance` | Date | Date de naissance |
| `num_cin` | String(8) | CIN |
| `num_passeport` | String(20) | Passeport |
| `entreprise_id` | Integer | Entreprise associée |
| `telephone` | String(30) | Téléphone |
| `code_nationalite` | String(3) | Code ISO nationalité |
| `code_specialite` | String(3) | Code spécialité |
| `date_delivrance` | Date | Date délivrance pièce |
| `lieu_nais_et` | String(100) | Lieu de naissance |
| `sexe` | String(1) | M/F |
| `lieu_delivrance` | String(100) | Lieu délivrance |
| `id_user` | Integer | Référence User |
| `adresse_postale` | String(255) | Adresse |
| `code_postal` | String(20) | Code postal |
| `ville` | String(100) | Ville |
| `gouvernorat` | String(100) | Gouvernorat |
| `linkedin_id` | String(255) | ID LinkedIn |
| `linkedin_url` | String(500) | URL LinkedIn |
| `linkedin_data_id` | Integer | Données LinkedIn |
| `email_esprit_etudiant` | String(100) | Email institutionnel |

### Endpoints

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/students/health` | Santé |
| POST | `/students/` | Créer étudiant |
| GET | `/students/{etudiant_id}` | Lire étudiant |
| GET | `/students/` | Rechercher (⚠️ bug route) |

**POST /students/**
```json
// Request
{
  "etudiant_id": "STU001",
  "email_etudiant": "ahmed.ben.ali@esprit.tn",
  "nom": "Ben Ali",
  "prenom": "Ahmed",
  "date_naissance": "2000-05-15",
  "num_cin": "12345678",
  "sexe": "M",
  "code_nationalite": "TUN",
  "code_specialite": "INF",
  "ville": "Tunis",
  "gouvernorat": "Tunis"
}

// Response 200
{
  "etudiant_id": "STU001",
  "email_etudiant": "ahmed.ben.ali@esprit.tn",
  "nom": "Ben Ali",
  "prenom": "Ahmed",
  "date_naissance": "2000-05-15",
  "num_cin": "12345678",
  "num_passeport": null,
  "sexe": "M",
  ...
}
```

**GET /students/?nom=Ben&prenom=Ahmed&email_etudiant=ahmed@**
```
⚠️ Erreur 500 — Conflit entre route /students/{etudiant_id} et /students/?params
```

### ⚠️ BUGS STUDENT-SERVICE

| # | Sévérité | Description | Correction |
|---|---------|-------------|-----------|
| B1 | 🔴 CRITIQUE | **Route conflict** : `GET /students/` (search) vs `GET /students/{etudiant_id}` — FastAPI route en premier → 500 | Renommer en `/students/search` |
| B2 | 🟡 MOYEN | **Aucune validation** longueur `etudiant_id` > 10 chars | Ajouter validator Pydantic |
| B3 | 🟢 FAIBLE | **Pas d'endpoint de mise à jour** `PUT /students/{id}` | Ajouter |

**Correction B1** :
```python
# Renommer l'endpoint de recherche
@router.get("/search", response_model=list[StudentRead])
async def search_students(nom: Optional[str] = None, ...):
    ...
```

---

## ⛓️ 5. BLOCKCHAIN-SERVICE

**Fichier principal** : `blockchain-service/app/main.py`  
**Port local test** : 8005  
**Status test** : ⚠️ **DÉMARRAGE CONDITIONNEL** (requiert FABRIC_GATEWAY_HOST + PORT)

### Modèle de données

#### Table `diplome_blockchain_ext`
| Champ | Type | Description |
|-------|------|-------------|
| `id_diplome` | Integer PK | ID diplôme |
| `titre` | String(255) | Titre |
| `mention` | String(50) | Mention |
| `date_emission` | Date | Date émission |
| `annee_promotion` | String(20) | Année promo |
| `hash_sha256` | String(64) UNIQUE | Hash du PDF |
| `tx_id_fabric` | String(255) | TX ID Hyperledger |
| `ipfs_cid` | String(100) | CID IPFS |
| `statut` | String(50) | Statut |
| `blockchain_retry_count` | Integer | Compteur de tentatives |
| `blockchain_last_retry` | DateTime | Dernière tentative |
| `generation_mode` | String(20) | Mode: UPLOAD/MICRO |
| `template_id` | Integer | Template PDF |
| `institution_id` | Integer | Institution |
| `specialite_id` | String(3) | Spécialité |
| `uploaded_by` | Integer | Utilisateur |
| `created_at` | DateTime | Date création |
| `updated_at` | DateTime | Dernière MAJ |

### Endpoints

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/blockchain/health` | Santé |
| POST | `/blockchain/diplome` | Enregistrer diplôme sur blockchain |
| GET | `/blockchain/diplome/{id}` | Lire enregistrement blockchain |
| GET | `/blockchain/diplomes` | Lister (filtre `?institution_id=`) |

**POST /blockchain/diplome — Payload COMPLET requis**
```json
{
  "id_diplome": 1,
  "titre": "Master en Informatique",
  "mention": "Très Bien",
  "date_emission": "2024-06-15",
  "annee_promotion": "2023-2024",
  "hash_sha256": "abc123def456abc123def456abc123def456abc123def456abc123def456abc1",
  "tx_id_fabric": "TX_FABRIC_ABC123456",
  "ipfs_cid": "QmTestCID123456789",
  "statut": "ORIGINAL",
  "blockchain_retry_count": 0,
  "blockchain_last_retry": null,
  "generation_mode": "UPLOAD",
  "template_id": 1,
  "institution_id": 1,
  "specialite_id": "INF",
  "uploaded_by": 1,
  "created_at": "2024-06-15T10:00:00",
  "updated_at": null
}

// Response 200
{
  "id_diplome": 1,
  "titre": "Master en Informatique",
  ...
}
```

### ⚠️ BUGS BLOCKCHAIN-SERVICE

| # | Sévérité | Description | Correction |
|---|---------|-------------|-----------|
| B1 | 🔴 CRITIQUE | **Variables d'env obligatoires non-optionnelles** (`FABRIC_GATEWAY_HOST`, `FABRIC_GATEWAY_PORT`) — crash sans elles | Ajouter valeurs par défaut dans config |
| B2 | 🔴 CRITIQUE | **Bug `text()` + concaténation string** pour `GET /blockchain/diplomes` — erreur SQLAlchemy | `text()` retourne un objet non concaténable → utiliser `select()` |
| B3 | 🟡 MOYEN | **Schéma très verbose** — tous les champs requis sans valeur par défaut | Rendre `Optional` les champs nullable |
| B4 | 🟢 FAIBLE | **Aucune intégration Fabric réelle** — service stocke juste en DB | Implémenter appel gRPC Fabric |

**Correction B1** (config.py) :
```python
class Settings(BaseSettings):
    DATABASE_URL: str
    FABRIC_GATEWAY_HOST: str = "localhost"  # Valeur par défaut
    FABRIC_GATEWAY_PORT: int = 7051         # Valeur par défaut
    FABRIC_CHANNEL: str = "channel-esprit"
    FABRIC_CHAINCODE: str = "diplochain-cc"
```

**Correction B2** (blockchain.py) :
```python
# AVANT (bugué)
query = text("SELECT * FROM diplome_blockchain_ext")
query += " WHERE institution_id = :inst"  # ← TypeError!

# APRÈS (correct)
from sqlalchemy import select
query = select(DiplomaBlockchain)
if institution_id is not None:
    query = query.where(DiplomaBlockchain.institution_id == institution_id)
result = await db.execute(query)
return result.scalars().all()
```

**Correction B3** (schemas.py) :
```python
class DiplomaBlockchainBase(BaseModel):
    titre: Optional[str] = None         # ← ajouter = None
    mention: Optional[str] = None
    annee_promotion: Optional[str] = None
    tx_id_fabric: Optional[str] = None
    blockchain_retry_count: Optional[int] = 0
    blockchain_last_retry: Optional[datetime] = None
    generation_mode: Optional[str] = None
    template_id: Optional[int] = None
    specialite_id: Optional[str] = None
    uploaded_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

---

## 💾 6. STORAGE-SERVICE

**Fichier principal** : `storage-service/app/main.py`  
**Port local test** : 8006  
**Status test** : ✅ **PARTIELLEMENT FONCTIONNEL** (GET /files/{cid} bug)

### Modèles de données

#### Table `ipfs_files`
| Champ | Type | Description |
|-------|------|-------------|
| `file_id` | Integer PK | Identifiant |
| `cid` | String(255) UNIQUE | CID IPFS |
| `status` | String(50) | PINNED, UNPINNED, PENDING |

#### Table `pinning_status`
| Champ | Type | Description |
|-------|------|-------------|
| `pin_id` | Integer PK | Identifiant |
| `cid` | String(255) | CID IPFS |
| `status` | String(50) | Statut épinglage |

### Endpoints

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/storage/health` | Santé |
| POST | `/storage/files` | Enregistrer un fichier IPFS |
| GET | `/storage/files/{cid}` | Récupérer info par CID (⚠️ bug) |

**POST /storage/files**
```json
// Request
{ "cid": "QmTestIPFSCID1234567", "status": "PINNED" }

// Response 200
{ "file_id": 1, "cid": "QmTestIPFSCID1234567", "status": "PINNED" }
```

### ⚠️ BUGS STORAGE-SERVICE

| # | Sévérité | Description | Correction |
|---|---------|-------------|-----------|
| B1 | 🔴 CRITIQUE | **`GET /storage/files/{cid}` retourne 500** — `result.scalars().first()` retourne un `Row`, pas un objet ORM | Utiliser `select(IPFSFile).where(IPFSFile.cid == cid)` |
| B2 | 🟡 MOYEN | **Aucune intégration IPFS réelle** — ne fait que stocker le CID en DB | Intégrer appel API IPFS kubo |

**Correction B1** :
```python
@router.get("/files/{cid}", response_model=IPFSFileRead)
async def get_file(cid: str, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    result = await db.execute(select(IPFSFile).where(IPFSFile.cid == cid))
    f = result.scalar_one_or_none()
    if not f:
        raise HTTPException(status_code=404, detail="CID not found")
    return f
```

---

## 📄 7. DOCUMENT-SERVICE

**Fichier principal** : `document-service/app/main.py`  
**Port local test** : 8007  
**Status test** : ✅ **FONCTIONNEL**  
**Note** : Ce service gère des "rapports" (pas des documents IPFS)

### Modèles de données

#### Table `rapport`
| Champ | Type | Description |
|-------|------|-------------|
| `id_rapport` | Integer PK | Identifiant |
| `nom_documents` | String(255) | Nom du rapport |
| `id_langue` | Integer | Langue |
| `id_type_impression` | Integer | Type d'impression |
| `id_annee` | Integer | Année |
| `etat` | Boolean | Actif/Inactif |
| `code_rapport` | String(25) UNIQUE | Code unique |

#### Table `rapport_institution` (pivot)
| Champ | Type | Description |
|-------|------|-------------|
| `id_rapport` | FK(rapport) PK | Rapport |
| `institution_id` | Integer PK | Institution |

### Endpoints

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/rapports/health` | Santé |
| POST | `/rapports/` | Créer rapport (dict libre) |
| GET | `/rapports/{id}` | Lire rapport |
| GET | `/rapports/` | Lister rapports (filtre `?code=`) |

**POST /rapports/**
```json
// Request (dict libre — PROBLÈME: pas de schema Pydantic)
{
  "nom_documents": "Rapport Annuel 2024",
  "id_langue": 1,
  "id_type_impression": 1,
  "id_annee": 2024,
  "etat": true,
  "code_rapport": "RPT-2024-001"
}

// Response 200
{ "id_rapport": 1 }
```

### ⚠️ BUGS DOCUMENT-SERVICE

| # | Sévérité | Description | Correction |
|---|---------|-------------|-----------|
| B1 | 🔴 CRITIQUE | **`main.py` incomplet** — manquait le corps `on_startup` | ✅ Corrigé |
| B2 | 🟡 MOYEN | **Endpoints utilisent `dict` brut** — aucune validation Pydantic | Créer `RapportCreate` et `RapportRead` schémas |
| B3 | 🟡 MOYEN | **Nom trompeur** : service s'appelle `document-service` mais route `/rapports/` — incohérence | Aligner nom ou ajouter route `/documents/` |
| B4 | 🟢 FAIBLE | `GET /rapports/{id}` retourne `__dict__` avec champs ORM internes | Utiliser `RapportRead` schema |

---

## 🏢 8. ENTREPRISE-SERVICE

**Fichier principal** : `entreprise-service/app/main.py`  
**Port local test** : 8008  
**Status test** : ✅ **FONCTIONNEL**

### Modèle de données

#### Table `entreprise`
| Champ | Type | Description |
|-------|------|-------------|
| `id` | Integer PK | Identifiant |
| `nom_entreprise` | String(200) INDEX | Nom |
| `secteur_activite` | String(200) | Secteur |
| `matricule_fiscale` | String(50) UNIQUE | MF |
| `email_contact` | String(100) | Email RH |
| `telephone` | String(30) | Téléphone |
| `adresse` | Text | Adresse complète |
| `site_web` | String(255) | Site web |
| `id_user` | Integer | Utilisateur admin |

### Endpoints

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/entreprises/health` | Santé |
| POST | `/entreprises/` | Créer entreprise |
| GET | `/entreprises/{id}` | Lire entreprise |
| GET | `/entreprises/` | Rechercher (filtre `?nom_entreprise=`) |

**POST /entreprises/**
```json
// Request
{
  "nom_entreprise": "Sofrecom Tunisie",
  "secteur_activite": "Télécommunications",
  "matricule_fiscale": "1234567A",
  "email_contact": "rh@sofrecom.tn",
  "telephone": "+216 71 234 567",
  "site_web": "https://sofrecom.com"
}

// Response 200
{
  "id": 1,
  "nom_entreprise": "Sofrecom Tunisie",
  "secteur_activite": "Télécommunications",
  "matricule_fiscale": "1234567A",
  "email_contact": "rh@sofrecom.tn",
  "telephone": "+216 71 234 567",
  "adresse": null,
  "site_web": "https://sofrecom.com",
  "id_user": null
}
```

### ⚠️ BUGS ENTREPRISE-SERVICE

| # | Sévérité | Description | Correction |
|---|---------|-------------|-----------|
| B1 | 🟡 MOYEN | **Même route conflict** que student-service: `GET /` vs `GET /{id}` | Tester `?nom_entreprise=` avec care |
| B2 | 🟢 FAIBLE | **Pas d'endpoint PUT** pour mettre à jour une entreprise | Ajouter |

---

## 🔔 9. NOTIFICATION-SERVICE

**Fichier principal** : `notification-service/app/main.py`  
**Port local test** : 8009  
**Status test** : ✅ **PARTIELLEMENT FONCTIONNEL** (`GET /user/{id}` bug)

### Modèle de données

#### Table `notification`
| Champ | Type | Description |
|-------|------|-------------|
| `id` | Integer PK | Identifiant |
| `user_id` | Integer INDEX | Utilisateur destinataire |
| `type_notification` | String(50) | EMAIL, SMS, ALERT |
| `message` | String(500) | Contenu |
| `status` | String(20) DEFAULT 'PENDING' | PENDING, SENT, FAILED |
| `created_at` | DateTime DEFAULT utcnow | Date création |

### Endpoints

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/notifications/health` | Santé |
| POST | `/notifications/` | Créer notification |
| GET | `/notifications/{id}` | Lire notification |
| GET | `/notifications/user/{user_id}` | Notifications par utilisateur (⚠️) |

**POST /notifications/**
```json
// Request
{
  "user_id": 1,
  "type_notification": "EMAIL",
  "message": "Votre diplôme a été certifié sur la blockchain.",
  "status": "PENDING"
}

// Response 200
{
  "id": 1,
  "user_id": 1,
  "type_notification": "EMAIL",
  "message": "Votre diplôme a été certifié sur la blockchain.",
  "status": "PENDING",
  "created_at": "2026-03-17T08:58:24.450726"
}
```

### ⚠️ BUGS NOTIFICATION-SERVICE

| # | Sévérité | Description | Correction |
|---|---------|-------------|-----------|
| B1 | 🔴 CRITIQUE | **`GET /notifications/user/{user_id}`** — `result.scalars().all()` sur un `text()` → erreur | Utiliser ORM select ou `result.mappings().all()` |
| B2 | 🟡 MOYEN | **Aucun envoi réel** — ne fait que stocker en DB | Intégrer SMTP/SendGrid/SMS |
| B3 | 🟢 FAIBLE | **Pas d'endpoint de mise à jour statut** — pour marquer comme SENT/FAILED | Ajouter `PATCH /notifications/{id}/status` |

**Correction B1** :
```python
@router.get("/user/{user_id}", response_model=list[NotificationRead])
async def get_user_notifications(user_id: int, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    result = await db.execute(
        select(Notification).where(Notification.user_id == user_id)
    )
    return result.scalars().all()
```

---

## 📊 10. ANALYTICS-SERVICE

**Fichier principal** : `analytics-service/app/main.py`  
**Port local test** : 8010  
**Status test** : ✅ **FONCTIONNEL** (retourne liste vide si table vide)

### Modèles de données

#### Table `dashboard_metrics_daily`
| Champ | Type | Description |
|-------|------|-------------|
| `metric_date` | Date PK | Date de la métrique |
| `nb_diplomes_emis` | Integer | Diplômes émis |
| `nb_diplomes_microservice` | Integer | Via microservice |
| `nb_diplomes_upload` | Integer | Via upload |
| `nb_nouveaux_etudiants` | Integer | Nouveaux étudiants |
| `nb_institutions_actives` | Integer | Institutions actives |
| `nb_diplomes_confirmes` | Integer | Confirmés |
| `nb_diplomes_pending` | Integer | En attente |
| `nb_diplomes_revoques` | Integer | Révoqués |
| `nb_verifications` | Integer | Vérifications effectuées |
| `updated_at` | DateTime | Dernière MAJ |

### Endpoints

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/analytics/health` | Santé |
| GET | `/analytics/metrics/daily` | Métriques journalières |

**GET /analytics/metrics/daily**
```json
// Response 200
[
  {
    "metric_date": "2024-06-15",
    "nb_diplomes_emis": 145,
    "nb_diplomes_microservice": 120,
    "nb_diplomes_upload": 25,
    "nb_nouveaux_etudiants": 30,
    "nb_institutions_actives": 5,
    "nb_diplomes_confirmes": 140,
    "nb_diplomes_pending": 3,
    "nb_diplomes_revoques": 2,
    "nb_verifications": 87,
    "updated_at": "2024-06-15T23:59:00"
  }
]
```

### ⚠️ BUGS ANALYTICS-SERVICE

| # | Sévérité | Description | Correction |
|---|---------|-------------|-----------|
| B1 | 🟡 MOYEN | **Aucune alimentation automatique** — les métriques ne se calculent pas | Ajouter job periodique ou trigger DB |
| B2 | 🟡 MOYEN | **Pas de filtre par période** — ni date range | Ajouter `?from=&to=` |
| B3 | 🟢 FAIBLE | **Modèles `InstitutionStatistics` et `StudentStatistics`** définis mais jamais utilisés | Ajouter endpoints |

---

## 🛡️ 11. ADMIN-DASHBOARD-SERVICE

**Fichier principal** : `admin-dashboard-service/app/main.py`  
**Port local test** : 8011  
**Status test** : ⚠️ **`GET /admin/dashboard` ERREUR 500**

### Modèle de données

#### Table `dashboard_metrics_daily` (même que analytics-service)
| Champ | Type | Description |
|-------|------|-------------|
| `metric_date` | Date PK | Date |
| `nb_diplomes_emis` | Integer | Diplômes émis |
| `nb_nouveaux_etudiants` | Integer | Nouveaux étudiants |
| `nb_institutions_actives` | Integer | Institutions actives |
| `nb_diplomes_confirmes` | Integer | Confirmés |
| `nb_diplomes_pending` | Integer | En attente |
| `updated_at` | DateTime | MAJ |

### Endpoints

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/admin/health` | Santé |
| GET | `/admin/dashboard` | Métriques dashboard (⚠️ bug) |
| GET | `/admin/diplomas` | Liste diplômes (mock) |
| GET | `/admin/students` | Liste étudiants (mock) |
| GET | `/admin/institutions` | Liste institutions (mock) |

### ⚠️ BUGS ADMIN-DASHBOARD-SERVICE

| # | Sévérité | Description | Correction |
|---|---------|-------------|-----------|
| B1 | 🔴 CRITIQUE | **`GET /admin/dashboard` → 500** — `result.scalars().all()` sur `text()` → incompatible SQLAlchemy | Utiliser `result.mappings().all()` |
| B2 | 🔴 CRITIQUE | **Modèle incomplet** — `DashboardMetricsDaily` dans admin n'a que 5 champs vs 10 dans analytics | Unifier les modèles |
| B3 | 🟡 MOYEN | **Endpoints /diplomas, /students, /institutions** — retournent des mocks hardcodés | Implémenter vraies requêtes ou appels inter-services |
| B4 | 🟢 FAIBLE | **Paramètre `?period=today`** ignoré dans la requête | Implémenter logique de filtre temporel |

**Correction B1** :
```python
@router.get("/dashboard", response_model=List[DashboardMetricsDailyRead])
async def get_dashboard_metrics(period: Optional[str] = "today", db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    result = await db.execute(
        select(DashboardMetricsDaily).order_by(DashboardMetricsDaily.metric_date.desc()).limit(30)
    )
    return result.scalars().all()
```

---

## ✅ 12. VERIFICATION-SERVICE

**Fichier principal** : `verification-service/app/main.py`  
**Port local test** : 8012  
**Status test** : ⚠️ **`POST /verify/qr` requiert `created_at` obligatoire** — bug schema

### Modèles de données

#### Table `qr_code_records`
| Champ | Type | Description |
|-------|------|-------------|
| `qr_code_records_id` | Integer PK | Identifiant |
| `diplome_id` | Integer | Diplôme associé |
| `etudiant_id` | String(10) | Étudiant |
| `qr_code_path` | String(255) | Chemin image QR |
| `identifiant_opaque` | String(255) UNIQUE | Code opaque de vérification |
| `url_verification` | String(500) | URL publique de vérification |
| `created_at` | DateTime | Date création |

#### Table `historique_operations`
| Champ | Type | Description |
|-------|------|-------------|
| `historique_operations_id` | Integer PK | Identifiant |
| `diplome_id` | Integer | Diplôme |
| `type_operation` | String(50) | CREATION, VERIFICATION, REVOCATION |
| `ancien_hash` | String(64) | Ancien hash |
| `nouvel_hash` | String(64) | Nouveau hash |
| `tx_id_fabric` | String(255) | TX ID |
| `acteur_id` | Integer | Acteur |
| `ip_address` | String(45) | IP source |
| `ms_tenant_id` | String(255) | Tenant ID |
| `commentaire` | String | Commentaire |
| `user_agent` | String | User-Agent navigateur |
| `timestamp` | DateTime | Horodatage |

### Endpoints

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/verify/health` | Santé |
| POST | `/verify/qr` | Créer enregistrement QR |
| GET | `/verify/qr/{qr_id}` | Lire QR record |
| GET | `/verify/diploma/{diploma_id}` | Vérifier diplôme (proxy blockchain) |
| POST | `/verify/history` | Enregistrer opération |

**POST /verify/qr**
```json
// Request (created_at requis — BUG: devrait être auto)
{
  "diplome_id": 1,
  "etudiant_id": "STU001",
  "qr_code_path": "/qr/diplome_1.png",
  "identifiant_opaque": "OPAQUE_ABC123XYZ",
  "url_verification": "https://verify.diplochain.tn/OPAQUE_ABC123XYZ",
  "created_at": "2026-03-17T09:00:00"
}

// Response 200
{
  "qr_code_records_id": 1,
  "diplome_id": 1,
  "etudiant_id": "STU001",
  "qr_code_path": "/qr/diplome_1.png",
  "identifiant_opaque": "OPAQUE_ABC123XYZ",
  "url_verification": "https://verify.diplochain.tn/OPAQUE_ABC123XYZ",
  "created_at": "2026-03-17T09:00:00"
}
```

### ⚠️ BUGS VERIFICATION-SERVICE

| # | Sévérité | Description | Correction |
|---|---------|-------------|-----------|
| B1 | 🟡 MOYEN | **`created_at` obligatoire** dans le schéma alors qu'il devrait être auto | Rendre `Optional[datetime] = None` dans schema, définir dans le router |
| B2 | 🟡 MOYEN | **`POST /verify/history`** utilise `HistoriqueOperationRead` comme input — inclut le PK | Créer `HistoriqueOperationCreate` sans le PK |
| B3 | 🟢 FAIBLE | **Proxy `GET /verify/diploma/{id}`** — retourne seulement `{"blockchain": ...}` sans vérification IPFS | Intégrer logique complète comme qr-validation-service |

---

## 📄 13. PDF-GENERATOR-SERVICE

**Fichier principal** : `pdf-generator-service/app/main.py`  
**Port local test** : 8013  
**Status test** : ✅ **FONCTIONNEL** (génère PDF via ReportLab)

### Modèles Pydantic

```python
StudentData: { nom, prenom, date_naissance, numero_etudiant }
DiplomaData: { titre, mention, date_emission, annee_promotion }
InstitutionData: { nom, logo_url, responsable }
GenerateRequest: { template_id, student, diploma, institution }
```

### Endpoints

| Méthode | Route | Réponse |
|---------|-------|---------|
| GET | `/pdf/health` | `{"status": "healthy"}` |
| POST | `/pdf/generate-diploma` | `application/pdf` (binaire) |

**POST /pdf/generate-diploma**
```json
// Request
{
  "template_id": "template-001",
  "student": {
    "nom": "Ben Ali",
    "prenom": "Ahmed",
    "date_naissance": "2000-05-15",
    "numero_etudiant": "STU001"
  },
  "diploma": {
    "titre": "Master en Informatique",
    "mention": "Très Bien",
    "date_emission": "2024-06-15",
    "annee_promotion": "2023-2024"
  },
  "institution": {
    "nom": "Esprit School of Engineering",
    "logo_url": "https://esprit.tn/logo.png",
    "responsable": "Dr. Mohamed Kamel"
  }
}

// Response 200 Content-Type: application/pdf
// Fichier PDF binaire (1548 bytes en test)
```

### ⚠️ BUGS PDF-GENERATOR-SERVICE

| # | Sévérité | Description | Correction |
|---|---------|-------------|-----------|
| B1 | 🟡 MOYEN | **PDF très basique** (ReportLab canvas simple) — pas de template réel | Intégrer WeasyPrint + templates HTML/CSS |
| B2 | 🟡 MOYEN | **`template_id` non utilisé** dans la génération | Implémenter sélection de template |
| B3 | 🟢 FAIBLE | **Pas de QR Code intégré** dans le PDF | Intégrer CID IPFS comme QR dans le PDF |

---

## 🔍 14. QR-VALIDATION-SERVICE

**Fichier principal** : `qr-validation-service/app/main.py`  
**Port local test** : 8014  
**Status test** : ✅ **FONCTIONNEL** (dépend de blockchain-service)

### Endpoints

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/qr/health` | Santé |
| GET | `/qr/verify/{identifiant_opaque}` | Vérifier diplôme (blockchain + IPFS) |

**GET /qr/verify/{identifiant_opaque}**

```
Logique de vérification V6 :
1. Query Hyperledger Fabric → hash_sha256 + ipfs_cid
2. Télécharger PDF depuis IPFS
3. Calculer SHA-256 du PDF téléchargé
4. Comparer les hashes

Si blockchain unavailable → 503
```

```json
// Response 200 (blockchain dispo)
{
  "is_valid": true,
  "identifiant_opaque": "OPAQUE_ABC123",
  "message": "Valid",
  "details": {
    "hash_on_chain": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "calculated_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "ipfs_cid": "QmTest123456789"
  }
}

// Response 503 (blockchain indisponible)
{ "detail": "Blockchain service unavailable" }
```

### ⚠️ BUGS QR-VALIDATION-SERVICE

| # | Sévérité | Description | Correction |
|---|---------|-------------|-----------|
| B1 | 🟡 MOYEN | **URL Fabric hardcodée**: `/blockchain/query/{id}` — endpoint n'existe pas dans blockchain-service | Créer cet endpoint dans blockchain-service |
| B2 | 🟡 MOYEN | **Fallback mock données** en cas d'erreur blockchain → toujours invalide (hash vide ≠ hash vide d'IPFS vide par coincidence) | Améliorer logique fallback |
| B3 | 🟢 FAIBLE | **IPFS timeout très court** (2 secondes) | Augmenter à 10s |

---

## ⚙️ 15. RETRY-WORKER-SERVICE

**Fichier principal** : `retry-worker-service/app/main.py`  
**Type** : Worker asynchrone (pas une API REST)  
**Status test** : Non testable sans PostgreSQL

### Fonctionnement

Worker qui tourne en boucle toutes les 60 secondes :
1. Recherche diplômes avec `statut = 'PENDING_BLOCKCHAIN'` et `blockchain_retry_count < 5`
2. Tente d'enregistrer sur Hyperledger Fabric
3. Incrémente le compteur de tentatives si échec

### ⚠️ BUGS RETRY-WORKER-SERVICE

| # | Sévérité | Description | Correction |
|---|---------|-------------|-----------|
| B1 | 🔴 CRITIQUE | **Requête SQL sur table `diplomes`** mais champ `diplome_id` n'existe pas (PK est `id` dans diploma-service) | Aligner les noms de colonnes |
| B2 | 🔴 CRITIQUE | **Logique Fabric commentée** — ne fait qu'incrémenter le compteur | Implémenter l'appel Fabric via blockchain-service |
| B3 | 🟡 MOYEN | **`DATABASE_URL` OBLIGATOIRE sans défaut** — crash si non définie | Ajouter valeur par défaut |
| B4 | 🟢 FAIBLE | **Aucune API REST** — impossible de monitorer ou déclencher manuellement | Ajouter endpoints `/worker/status` et `/worker/trigger` |

---

## 🗺️ CARTE COMPLÈTE DES ENDPOINTS (chemins exacts pour tests)

### Via API Gateway (prefix `/api`)
```
# USER SERVICE
POST   /api/users/auth/login           → Login (form-data)
GET    /api/users/auth/me              → Profil courant (Bearer JWT)
POST   /api/users/                     → Créer utilisateur
GET    /api/users/{user_id}            → Lire utilisateur
PUT    /api/users/{user_id}            → Modifier utilisateur
GET    /api/users/roles/               → Lister rôles
POST   /api/users/roles/               → Créer rôle
GET    /api/users/roles/{id_role}      → Lire rôle
PUT    /api/users/roles/{id_role}      → Modifier rôle

# INSTITUTION SERVICE  
POST   /api/institutions/              → Créer institution
GET    /api/institutions/              → Lister (?active=true/false)
GET    /api/institutions/{id}          → Lire institution
PUT    /api/institutions/{id}          → Modifier institution
POST   /api/institutions/{id}/blockchain → Config blockchain
GET    /api/institutions/{id}/students → Étudiants de l'institution

# STUDENT SERVICE
POST   /api/students/                  → Créer étudiant
GET    /api/students/{etudiant_id}     → Lire étudiant
GET    /api/students/                  → Rechercher (?nom=&prenom=&email=) ⚠️ BUG

# DIPLOMA SERVICE
POST   /api/diplomas/                  → Créer diplôme ⚠️ BUG UUID/SQLite
GET    /api/diplomas/{diploma_id}      → Lire diplôme (UUID)
PUT    /api/diplomas/{diploma_id}      → Modifier diplôme
POST   /api/diplomas/{diploma_id}/revoke → Révoquer

# BLOCKCHAIN SERVICE
POST   /api/blockchain/diplome         → Enregistrer sur blockchain ⚠️ Schéma verbose
GET    /api/blockchain/diplome/{id}    → Lire enregistrement
GET    /api/blockchain/diplomes        → Lister (?institution_id=) ⚠️ BUG text()

# STORAGE SERVICE
POST   /api/storage/files              → Enregistrer fichier IPFS
GET    /api/storage/files/{cid}        → Lire par CID ⚠️ BUG scalars()

# DOCUMENT SERVICE
POST   /api/documents/                 → Créer rapport ⚠️ dict brut
GET    /api/documents/{id}             → Lire rapport
GET    /api/documents/                 → Lister (?code=)

# ENTREPRISE SERVICE
POST   /api/entreprises/               → Créer entreprise
GET    /api/entreprises/{id}           → Lire entreprise
GET    /api/entreprises/               → Rechercher (?nom_entreprise=)

# NOTIFICATION SERVICE
POST   /api/notifications/             → Créer notification
GET    /api/notifications/{id}         → Lire notification
GET    /api/notifications/user/{user_id} → Par utilisateur ⚠️ BUG scalars()

# ANALYTICS SERVICE
GET    /api/analytics/metrics/daily    → Métriques journalières

# ADMIN DASHBOARD
GET    /api/admin/dashboard            → Dashboard métriques ⚠️ BUG scalars()
GET    /api/admin/diplomas             → Liste diplômes (mock)
GET    /api/admin/students             → Liste étudiants (mock)
GET    /api/admin/institutions         → Liste institutions (mock)

# VERIFICATION SERVICE
POST   /api/verify/qr                  → Créer enregistrement QR ⚠️ created_at requis
GET    /api/verify/qr/{qr_id}          → Lire QR record
GET    /api/verify/diploma/{id}        → Vérifier diplôme (proxy blockchain)
POST   /api/verify/history             → Enregistrer opération

# PDF GENERATOR
POST   /api/pdf/generate-diploma       → Générer PDF diplôme (→ binary PDF)

# QR VALIDATION
GET    /api/qr/verify/{identifiant_opaque} → Vérifier authenticité diplôme

# HEALTH CHECKS
GET    /health                         → Gateway health
GET    /api/users/users/               → User service health ⚠️ BUG double segment
```

### En accès direct (en dehors Gateway)
```
# Services sur ports locaux (test)
:8001  → user-service
:8002  → diploma-service
:8003  → institution-service
:8004  → student-service
:8005  → blockchain-service
:8006  → storage-service
:8007  → document-service
:8008  → entreprise-service
:8009  → notification-service
:8010  → analytics-service
:8011  → admin-dashboard-service
:8012  → verification-service
:8013  → pdf-generator-service
:8014  → qr-validation-service
```

---

## 🔴 RÉCAPITULATIF DES BUGS CRITIQUES (À CORRIGER EN PRIORITÉ)

| Priorité | Service | Bug | Impact |
|----------|---------|-----|--------|
| 🔴 P1 | **API Gateway** | URL proxy avec double segment (`/users/users/1`) | Tous les appels passent par gateway → KO |
| 🔴 P1 | **diploma-service** | `postgresql.UUID` incompatible avec SQLite | Service inutilisable sans PostgreSQL |
| 🔴 P1 | **diploma-service** | `main.py` incomplet (corrigé) | Service ne démarrait pas |
| 🔴 P1 | **blockchain-service** | `text()` + concaténation string → TypeError | `GET /blockchain/diplomes` → crash |
| 🔴 P1 | **blockchain-service** | Variables env Fabric obligatoires sans défaut | Service ne démarre pas sans `.env` |
| 🔴 P1 | **admin-dashboard** | `result.scalars()` sur `text()` → 500 | Dashboard inutilisable |
| 🔴 P1 | **retry-worker** | Champ `diplome_id` inexistant (`id` dans diplomes) | Worker ne traite rien |
| 🟡 P2 | **user-service** | Double `tokentype` dans modèle | Warning SQLAlchemy |
| 🟡 P2 | **user-service** | Route conflict `GET /users/` masque `list_users` | Liste utilisateurs inaccessible |
| 🟡 P2 | **student-service** | Route conflict `GET /students/` → 500 | Recherche étudiants KO |
| 🟡 P2 | **storage-service** | `scalars()` sur text query pour `GET /files/{cid}` → 500 | Lookup CID KO |
| 🟡 P2 | **notification-service** | `scalars()` sur text query pour `GET /user/{id}` → 500 | Notifications user KO |
| 🟡 P2 | **verification-service** | `created_at` requis dans schéma | QR creation nécessite date manuelle |
| 🟡 P2 | **blockchain-service** | Schéma trop verbose — tous champs requis | API difficile à utiliser |

---

## 🟢 SERVICES OPÉRATIONNELS (SANS CORRECTION)

| Service | Status | Endpoints fonctionnels |
|---------|--------|----------------------|
| user-service | ✅ | login, me, create/read/update user, CRUD roles |
| institution-service | ✅ | CRUD complet, blockchain config, proxy students |
| student-service | ⚠️ | create, read by ID (search cassé) |
| entreprise-service | ✅ | create, read, search |
| notification-service | ⚠️ | create, read by ID (user list cassé) |
| analytics-service | ✅ | health, metrics (vide si pas de données) |
| pdf-generator-service | ✅ | health, generate PDF |
| qr-validation-service | ✅ | health, verify (dépend blockchain) |

---

## 📁 LISTE DES FICHIERS CLÉS DU BACKEND V2

```
backend/app/v2/
├── api-gateway/
│   └── app/main.py                          ← Proxy + SERVICE_MAP
│
├── user-service/app/
│   ├── main.py                              ← Config FastAPI + routers
│   ├── core/config.py                       ← Settings (DATABASE_URL, JWT)
│   ├── core/database.py                     ← Engine SQLAlchemy async
│   ├── core/models.py                       ← User, Role, UserRole ⚠️ doublon tokentype
│   ├── core/schemas.py                      ← Pydantic schemas
│   ├── core/security.py                     ← bcrypt + JWT
│   ├── core/dependencies.py                 ← get_current_user, require_role
│   └── routers/
│       ├── users.py                         ← ⚠️ Route conflict
│       ├── auth.py                          ← Login + /me
│       └── roles.py                         ← CRUD rôles
│
├── diploma-service/app/
│   ├── main.py                              ← ✅ Corrigé (incomplet avant)
│   ├── core/models.py                       ← ⚠️ postgresql.UUID → incompatible SQLite
│   ├── core/schemas.py                      ← DiplomaCreate/Read/Update
│   └── routers/diplomas.py                  ← CRUD + revoke
│
├── institution-service/app/
│   ├── core/models.py                       ← Institution, BlockchainExt, SpecialiteExt
│   ├── core/schemas.py                      ← ⚠️ PUT utilise Read au lieu de Update
│   └── routers/institutions.py              ← CRUD + blockchain + proxy students
│
├── student-service/app/
│   ├── core/models.py                       ← Etudiant (30+ champs)
│   └── routers/students.py                  ← ⚠️ Route conflict search vs read
│
├── blockchain-service/app/
│   ├── core/config.py                       ← ⚠️ FABRIC vars obligatoires sans défaut
│   ├── core/models.py                       ← DiplomaBlockchain (15 champs)
│   ├── core/schemas.py                      ← ⚠️ Tous champs requis sans Optional
│   └── routers/blockchain.py                ← ⚠️ Bug text() concaténation
│
├── storage-service/app/
│   ├── core/models.py                       ← IPFSFile, PinningStatus
│   └── routers/storage.py                   ← ⚠️ Bug scalars() sur text()
│
├── document-service/app/
│   ├── main.py                              ← ✅ Corrigé
│   ├── core/models.py                       ← Rapport, RapportInstitution
│   └── routers/documents.py                 ← ⚠️ dict brut sans Pydantic
│
├── entreprise-service/app/
│   ├── core/models.py                       ← Entreprise
│   └── routers/entreprises.py               ← ⚠️ Route conflict potentiel
│
├── notification-service/app/
│   ├── core/models.py                       ← Notification
│   └── routers/notifications.py             ← ⚠️ Bug scalars() sur text()
│
├── analytics-service/app/
│   ├── core/models.py                       ← DashboardMetricsDaily + stats
│   └── routers/analytics.py                 ← GET metrics/daily
│
├── admin-dashboard-service/app/
│   ├── core/models.py                       ← ⚠️ Modèle incomplet vs analytics
│   └── routers/dashboard.py                 ← ⚠️ Bug scalars() + mocks
│
├── verification-service/app/
│   ├── core/models.py                       ← QrCodeRecord, HistoriqueOperation
│   ├── core/schemas.py                      ← ⚠️ created_at requis
│   └── routers/verify.py                    ← QR + history + proxy blockchain
│
├── pdf-generator-service/app/
│   └── main.py                              ← ReportLab (basique)
│
├── qr-validation-service/app/
│   └── main.py                              ← Logique V6 verify (blockchain + IPFS)
│
├── retry-worker-service/app/
│   └── main.py                              ← ⚠️ Worker incomplet (Fabric commenté)
│
└── docker-compose.v2.yml                    ← Orchestration complète
```

---

## 🛠️ SUGGESTIONS DE CORRECTION PRIORITAIRES

### Sprint 1 — Corrections critiques (blocants)

```python
# 1. API Gateway — Corriger URL proxy
url = f"{base}/{url_path}"  # Supprimer le /{service}/ redondant

# 2. blockchain-service/config.py — Valeurs par défaut
FABRIC_GATEWAY_HOST: str = "localhost"
FABRIC_GATEWAY_PORT: int = 7051

# 3. blockchain-service/routers/blockchain.py — Corriger text() + concat
query = select(DiplomaBlockchain)
if institution_id:
    query = query.where(DiplomaBlockchain.institution_id == institution_id)

# 4. admin-dashboard/routers/dashboard.py — Corriger scalars() 
result = await db.execute(select(DashboardMetricsDaily)...)
return result.scalars().all()

# 5. notification/storage — Même correction scalars()
result = await db.execute(select(Notification).where(...))
return result.scalars().all()
```

### Sprint 2 — Améliorations schema et routes

```python
# 6. student-service — Renommer route search
@router.get("/search", ...)  # au lieu de GET /

# 7. user-service — Route health dédié
@router.get("/health", ...)  # au lieu de GET /

# 8. blockchain-service/schemas.py — Tout Optional
class DiplomaBlockchainBase(BaseModel):
    annee_promotion: Optional[str] = None
    # ... tous les champs avec = None

# 9. verification-service/schemas.py — created_at auto
class QrCodeRecordBase(BaseModel):
    created_at: Optional[datetime] = None  # Pas requis
```

### Sprint 3 — Sécurité et authentification

```python
# 10. Sécuriser les endpoints sensibles
from core.dependencies import get_current_user, require_role

@router.post("/", dependencies=[Depends(require_role("INSTITUTION_ADMIN", "SUPER_ADMIN"))])
async def create_diploma(...):
    ...
```

---

## 📊 RÉSUMÉ DES TESTS

| Service | Health | CRUD | Bugs détectés |
|---------|--------|------|--------------|
| API Gateway | ✅ | ⚠️ URL bug | 1 critique |
| user-service | ✅ | ✅ | 2 moyens, route conflict |
| diploma-service | ✅ | ❌ UUID | 2 critiques |
| institution-service | ✅ | ✅ | 1 moyen |
| student-service | ✅ | ⚠️ | 1 critique route |
| blockchain-service | ✅ | ⚠️ | 2 critiques |
| storage-service | ✅ | ⚠️ | 1 critique GET |
| document-service | ✅ | ✅ | 1 moyen |
| entreprise-service | ✅ | ✅ | 0 |
| notification-service | ✅ | ⚠️ | 1 critique GET user |
| analytics-service | ✅ | ✅ | 0 |
| admin-dashboard | ✅ | ❌ | 2 critiques |
| verification-service | ✅ | ⚠️ | 1 moyen |
| pdf-generator | ✅ | ✅ | 0 |
| qr-validation | ✅ | ✅ | 1 moyen |
| retry-worker | ➖ | ➖ | 2 critiques |

**Légende**: ✅ OK | ⚠️ Partiellement fonctionnel | ❌ Erreur | ➖ Non testable
