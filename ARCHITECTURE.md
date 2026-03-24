# DiploChain Architecture

## 📐 High-Level Overview

DiploChain follows a modern microservices architecture with a decentralized trust layer provided by **Hyperledger Fabric**.

### Component Diagram (ASCII)
```text
                      +-------------------+
                      |   Web Dashboard   |
                      |   (React/Vite)    |
                      +---------+---------+
                                |
                                v REST / WebSocket
                      +---------+---------+
                      | Fabric API Server |
                      | (Node.js/Express) |
                      +----+---------+----+
                           |         |
           +---------------+         +---------------+
           |                                         |
           v SQL                                     v gRPC / CLI
+----------+----------+                   +----------+----------+
|      PostgreSQL     |                   | Hyperledger Fabric |
| (Off-chain History) |                   | (Private Ledger)   |
+---------------------+                   +--------------------+
```

## 🏗️ Technical Stack
- **Frontend**: React 18, Vite, React Router, Lucide Icons.
- **Backend API**: Express.js, Node-Fetch, PG (Postgres client).
- **Blockchain**: Hyperledger Fabric v2.5 (Channel: `channel-1`).
- **Chaincode**: Golang v1.21.
- **Database**: PostgreSQL 15 (Relational mapping for fast audit).
- **Storage**: IPFS (CID stored on-chain for document verification).

## 🔀 Data Flow
1. **Request**: UI sends transaction request to API Server.
2. **Endorsement**: API Server invokes Chaincode on the Peer.
3. **Commit**: Transaction is validated, ordered, and committed to the ledger.
4. **Mirroring**: API Server captures the event and updates the PostgreSQL history table for local audit.
