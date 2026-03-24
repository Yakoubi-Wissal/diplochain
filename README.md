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

## 🚀 Quick Start

### 1. Prerequisites
- Docker & Docker Compose
- Node.js (v18+)
- Go (v1.21+)

### 2. Launch Environment
```bash
# Clone the project
git clone https://github.com/your-repo/diplochain.git
cd diplochain

# Start the full stack (Infra + Network)
./run_diplochain.sh

# Start the API Server
cd fabric-api-server && npm install && npm start

# Start the Dashboard
# In a new terminal
cd audit-dashboard && npm install && npm run dev
```

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
