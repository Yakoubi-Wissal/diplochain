# 🎓 DiploChain V2

> **Secure, Decentralized, and Transparent Academic Diploma Management System.**

[![Hyperledger Fabric](https://img.shields.io/badge/Blockchain-Hyperledger%20Fabric%20v2.5-blue.svg)](https://www.hyperledger.org/use/fabric)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB.svg)](https://reactjs.org/)
[![Node.js](https://img.shields.io/badge/Backend-Node.js%20%2F%20Express-339933.svg)](https://nodejs.org/)

DiploChain is a production-ready solution for academic institutions to issue, verify, and revoke diplomas on a private blockchain. It eliminates diploma fraud and simplifies administrative audits.

---

## ✨ Key Features

- ⛓️ **Blockchain Integrity**: Immutable records using Hyperledger Fabric v2.5.
- 📊 **Dynamic Audit Dashboard**: Real-time monitoring of network health and transactions.
- 📜 **IPFS Integration**: Decentralized storage for diploma documents (PDFs).
- 🔍 **Instant Verification**: Public or private endpoints to verify hashes instantly.
- 🛡️ **Revocation Management**: Secure revocation flow with on-chain motif logging.
- 📑 **Automated Reporting**: Export project status and activities in JSON or PDF.

---

## 🏗️ Architecture

```text
      [ Admin / User ]
             |
             v
+-----------------------------+
|    React Dashboard (3001)   |  <-- Premium UI with Glassmorphism
+--------------+--------------+
               |
               v (REST API + JWT)
+--------------+--------------+      +--------------------------+
|   Fabric API Server (4001)  | <--> |  PostgreSQL (History DB) |
+--------------+--------------+      +--------------------------+
               |
               v (Docker Exec / Fabric CLI)
+--------------+--------------+
|  Hyperledger Fabric Network |  <-- Private Distributed Ledger
| (Orderer, Peer, CA, CouchDB)|
+-----------------------------+
```

For more detailed technical info, see:
- 🇫🇷 [Documentation Complète (FR)](./DOCUMENTATION_FR.md)
- 🇬🇧 [Full Technical Documentation (EN)](./DOCUMENTATION_EN.md)

---

## 🚀 Quick Start (One-Click Deployment)

The entire ecosystem (Blockchain, Databases, Microservices, and Dashboard) is now unified under a single orchestration.

### 1. Prerequisites
- Docker & Docker Compose (V2 recommended)

### 2. Launch Everything
```bash
# Clone and enter the project
git clone https://github.com/Yakoubi-Wissal/diplochain.git
cd diplochain

# Start the entire stack
docker-compose up -d --build
```

### 3. Access the Services
- **Audit Dashboard**: [http://localhost:3000](http://localhost:3000)
- **API Gateway (V2)**: [http://localhost:8000](http://localhost:8000)
- **Fabric API Server**: [http://localhost:4001](http://localhost:4001)
- **IPFS Node**: [http://localhost:5001/webui](http://localhost:5001/webui)

---

## 🛠️ Technology Stack

- **Blockchain**: Hyperledger Fabric (Go Chaincode)
- **Backend**: Node.js, Express, PostgreSQL
- **Frontend**: React, Vite, Tailwind-ready Vanilla CSS, Lucide Icons
- **Infrastructure**: Docker, Shell Scripting

---

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

---

## ⚖️ License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

*Developed with ❤️ for DiploChain Project.*
