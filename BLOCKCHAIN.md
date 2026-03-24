# DiploChain Blockchain Logic

## ⛓️ Network Topology
- **Organization**: `DiploChainOrgMSP`
- **Peer**: `peer0.diplochain.local`
- **Orderer**: `orderer.diplochain.local` (Raft Consensus)
- **State Database**: CouchDB (Rich query support)

---

## 📜 Chaincode: `diplochain` (v1.3)

### Core Functions

#### 1️⃣ `RegisterDiploma(id, hash, cid)`
- **Input**: Diploma ID, SHA-256 Hash of PDF, IPFS CID.
- **Logic**: Creates a `Diploma` asset on the ledger with timestamp.
- **Access**: Restricted to authorized institutions.

#### 2️⃣ `VerifyDiploma(id, incomingHash)`
- **Input**: Diploma ID, Hash to verify.
- **Logic**: Retrieves asset, compares hashes, and returns `VERIFIED` or `INVALID`.

#### 3️⃣ `RevokeDiploma(id, motif)`
- **Input**: Diploma ID, Reason for revocation.
- **Logic**: Updates `isRevoked` flag and appends motif. This action is irreversible.

---

## 🛠️ Transaction Security
- **Identity**: Transactions are signed by the Peer using MSP certificates.
- **Integrity**: Change logs are immutable and can be audited via `GetHistoryForKey`.
