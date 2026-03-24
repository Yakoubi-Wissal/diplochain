# DiploChain — fabric-network

Réseau Hyperledger Fabric 2.5 pour la plateforme DiploChain.  
Architecture : **1 institution = 1 canal Fabric** (isolé), chaincode `diplochain` déployé sur chaque canal.

---

## Structure des fichiers

```
fabric-network/
├── crypto-config.yaml          # Définition des organisations et peers
├── configtx.yaml               # Profils de canaux (genesis + institution)
├── docker-compose.fabric.yml   # Orderer + Peer + CouchDB + CA
├── .env                        # Variables d'environnement
├── bin/                        # Binaires Fabric (après install-fabric.sh)
├── crypto-config/              # Certificats générés (ignoré par git)
├── channel-artifacts/          # Blocs genesis et configs (ignoré par git)
├── chaincode/
│   └── diplochain/
│       ├── diplochain.go       # Smart contract Go
│       └── go.mod
└── scripts/
    ├── install-fabric.sh       # Téléchargement binaires Fabric 2.5
    ├── bootstrap.sh            # Initialisation réseau (1 seule fois)
    └── create-channel.sh       # Création canal par institution
```

---

## Démarrage rapide

### 1. Télécharger les binaires Fabric

```bash
cd fabric-network/
chmod +x scripts/*.sh
./scripts/install-fabric.sh
```

### 2. Initialiser le réseau

```bash
./scripts/bootstrap.sh
```

Ce script : génère les certificats (cryptogen) → crée le genesis block → démarre les conteneurs Docker.

### 3. Créer un canal pour une institution

```bash
# Quand institution_id = 42 s'inscrit sur DiploChain :
./scripts/create-channel.sh 42
```

Ce qui génère dans PostgreSQL :
```sql
UPDATE institution_blockchain_ext
SET channel_id = 'channel_42',
    peer_node_url = 'grpc://peer0.diplochain.local:7051'
WHERE institution_id = 42;
```

---

## Fonctions du chaincode

| Fonction | Appelant | Description |
|---|---|---|
| `RegisterDiploma(diplomeID, hashSHA256, ipfsCID, institutionID, etudiantID, dateEmission)` | blockchain-service | Ancre un diplôme on-chain, retourne TX_ID |
| `QueryDiploma(diplomeID)` | verification-service | Lit un diplôme par son ID |
| `VerifyDiploma(diplomeID, hashSHA256)` | verification-service | Vérifie authenticité + statut |
| `RevokeDiploma(diplomeID, motif)` | blockchain-service | Révoque un diplôme |
| `QueryByInstitution(institutionID)` | admin-dashboard-service | Liste diplômes d'une institution |
| `GetDiplomaHistory(diplomeID)` | verification-service | Historique des transactions |

---

## Ports exposés

| Service | Port | Usage |
|---|---|---|
| `orderer.diplochain.local` | 7050 | gRPC clients (blockchain-service) |
| `orderer.diplochain.local` | 7053 | Admin API (osnadmin) |
| `peer0.diplochain.local` | 7051 | gRPC peer (blockchain-service) |
| `couchdb0.diplochain.local` | 5984 | CouchDB UI (dev uniquement) |
| `fabric-ca.diplochain.local` | 7054 | Certificate Authority |

---

## Variables critiques PostgreSQL

La table `institution_blockchain_ext` lie chaque institution à son canal :

```sql
-- Après create-channel.sh 42 :
SELECT channel_id, peer_node_url FROM institution_blockchain_ext WHERE institution_id = 42;
-- channel_42 | grpc://peer0.diplochain.local:7051

-- Le blockchain-service lit cette table pour router les transactions :
SELECT channel_id FROM institution_blockchain_ext WHERE institution_id = $1;
```

---

## Sécurité

- TLS activé sur tous les services (peer, orderer, CA)
- `blockchain-service` non exposé publiquement (réseau Docker interne uniquement)
- Certificats MSP dans `./crypto-config/` — **ne jamais commiter ce dossier**
- Variables sensibles dans `.env` — **ne jamais commiter ce fichier en production**

---

## .gitignore recommandé

```
crypto-config/
channel-artifacts/
bin/
.env
```
