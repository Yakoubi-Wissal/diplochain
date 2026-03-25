# DiploChain V2 — Documentation Complète du Projet

## 1. Présentation du Projet
DiploChain est une plateforme décentralisée pour l'émission, la vérification et la révocation de diplômes académiques utilisant **Hyperledger Fabric**. Elle garantit l'immutabilité des enregistrements tout en offrant un tableau de bord d'audit en temps réel pour les administrateurs.

**Fonctionnalités clés :**
- **Immuabilité** : Chaque diplôme est haché et stocké sur un registre blockchain privé.
- **Vérification** : Les tiers peuvent vérifier instantanément l'authenticité d'un diplôme via des vérifications de hash.
- **Révocation** : Les institutions peuvent révoquer des diplômes en cas de fraude ou d'erreur.
- **Audit en temps réel** : Un tableau de bord dynamique surveillant la santé du réseau et le flux de transactions.

---

## 2. Architecture

### Schéma d'Architecture Globale
```text
      [ UTILISATEUR / ADMIN ]
                 |
                 v
+-----------------------------+
|   Dashboard React (3001)    |  <-- Frontend (UI/UX)
+--------------+--------------+
               |
               v (REST / JWT)
+--------------+--------------+      +--------------------------+
|  Serveur API Fabric (4001)  | <--> |  PostgreSQL (Historique) |
+--------------+--------------+      +--------------------------+
               |
               v (Docker Exec / Fabric Ops)
+--------------+--------------+
|   Réseau Hyperledger Fabric |  <-- Registre Privé
| (Orderer, Peer, CA, CouchDB)|
+-----------------------------+
```

### Interaction des Composants
1.  **Frontend** : Le client React interroge le serveur API pour obtenir des statistiques et déclencher des transactions.
2.  **Serveur API** : Pont central. Gère les requêtes DB pour l'historique et exécute les commandes CLI Fabric à l'intérieur des conteneurs pour les opérations blockchain.
3.  **Réseau Fabric** : Exécute le chaincode GOLANG et maintient l'état du monde dans CouchDB.
4.  **PostgreSQL** : Stocke les métadonnées, les journaux d'audit et les sessions utilisateurs pour une récupération rapide.

---

## 3. Guide d'Installation

### Prérequis
- Docker & Docker Compose
- Node.js (v18+)
- Golang (v1.21+)
- WSL2 (si sur Windows)

### Étapes d'Installation
1.  **Cloner le dépôt** :
    ```bash
    git clone https://github.com/Yakoubi-Wissal/diplochain.git
    cd diplochain
    ```
2.  **Démarrer l'Infrastructure** :
    ```bash
    ./run_diplochain.sh
    ```
3.  **Initialiser le Backend** :
    ```bash
    cd fabric-api-server
    npm install
    npm start
    ```
4.  **Initialiser le Frontend** :
    ```bash
    cd audit-dashboard
    npm install
    npm run dev
    ```

---

## 4. Variables d'Environnement
Fichier `.env` global (dans `fabric-network/.env`) :
- `COUCHDB_PASSWORD` : Mot de passe pour les instances CouchDB.
- `FABRIC_VERSION` : ex, `2.5`.
- `CHAINCODE_VERSION` : Version stable actuelle (`1.3`).
- `ORDERER_ADDRESS` : Adresse GRPC de l'orderer.

---

## 5. Documentation Backend (API)

### Exemples de Points de Terminaison
- **GET `/api/fabric/stats`** : Retourne les compteurs en temps réel.
- **POST `/api/fabric/chaincode/invoke`** :
  - Corps : `{ "fn": "RegisterDiploma", "args": ["D-123", "Hash..."] }`
  - Retour : `{ "success": true, "txId": "..." }`

---

## 6. Logique Blockchain

### Fonctions du Chaincode (GOLANG)
- **RegisterDiploma** : Sérialise les métadonnées du diplôme et les stocke avec `PutState`.
- **VerifyDiploma** : Récupère le diplôme par ID et compare le hash fourni.
- **RevokeDiploma** : Définit le drapeau `isRevoked` et enregistre le motif de révocation.

### Flux de Séquence de Transaction
```text
Frontend -> Serveur API -> Docker Exec (Peer) -> Chaincode (Invoke) -> Endossement -> Commit -> Ledger
```

---

## 7. Schéma de Base de Données
- **User** : Identifiants et sessions JWT.
- **historique_operations** : Suivi des transactions blockchain (cache hors-chaîne).
- **institution_blockchain_ext** : Correspondance entre les institutions DB et les canaux Fabric.

---

## 8. Dépannage (Troubleshooting)
- **API 500** : Vérifier les permissions de `diplochain_user` dans Postgres.
- **Timeouts Fabric** : S'assurer que `peer0.diplochain.local` tourne (`docker ps`).
- **Échec d'enregistrement du Chaincode** : Vérifier que `diplochain.go` n'utilise pas de types non supportés (pointeurs, time.Time).

---

## 9. Déploiement
- **Local** : Utiliser `docker-compose.yml` et `npm run dev`.
- **Production** : Recommandé d'utiliser Kubernetes (K8s) pour les nœuds Fabric et un proxy Nginx de qualité production pour le frontend.

---
*Généré par l'Architecte Technique DiploChain.*
