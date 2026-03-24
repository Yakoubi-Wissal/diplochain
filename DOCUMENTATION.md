# DiploChain — Master Documentation Guide

This document serves as the primary technical entry point for the DiploChain project.

---

## 🧭 Navigation

- 📊 **[API.md](./API.md)** — Detailed REST API endpoints and payload examples.
- 📐 **[ARCHITECTURE.md](./ARCHITECTURE.md)** — System design, data flows, and technical stack.
- ⛓️ **[BLOCKCHAIN.md](./BLOCKCHAIN.md)** — Hyperledger Fabric topology and Chaincode logic.
- 🚀 **[README.md](./README.md)** — Quick start and project overview.
- 🇫🇷 **[DOCUMENTATION_FR.md](./DOCUMENTATION_FR.md)** — Manuel technique complet (Français).

---

## 📑 Use Case: PFE Academic Submission
This project is designed as a template for **Senior Academic Projects (PFE)**. It demonstrates:
1. **Full-stack Integration**: React + Node.js + PostgreSQL.
2. **Blockchain Implementation**: Permissioned ledger with Hyperledger Fabric.
3. **Auditability**: Off-chain history mirroring for fast reporting.
4. **Microservices Design**: Decoupled components communicating via REST.

---

## 🛠️ Maintenance & Operations
- **Redeploy Chaincode**: Use `./scripts/redeploy_chaincode.sh`.
- **Seed Data**: Use `./scripts/seed_and_fix.sh`.
- **Full Refresh**: Use `./run_diplochain.sh`.

---
*Status: READY FOR DEPLOYMENT • Version: 1.5.0*
