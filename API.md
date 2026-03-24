# DiploChain API Reference

## 🌐 Base URL
Default: `http://localhost:4001`

---

## 🔒 Authentication
Endpoints protected by JWT must include:
`Authorization: Bearer <token>`

---

## ⛓️ Blockchain Operations

### POST `/api/fabric/chaincode/invoke`
Executes a function on the Fabric network.
- **Body**:
  ```json
  {
    "channel": "channel-1",
    "fn": "RegisterDiploma",
    "args": ["D-123", "SHA256_HASH", "IPFS_CID"]
  }
  ```
- **Response**: `200 OK` with transaction details.

### GET `/api/fabric/stats`
Returns aggregated counts for the dashboard.
- **Response**:
  ```json
  {
    "total_tx": 150,
    "diplomas": 90,
    "verifications": 45,
    "revocations": 15
  }
  ```

---

## 📊 Monitoring & Reports

### GET `/api/fabric/network/status`
Health check for Fabric nodes (Orderer, Peer, CA).

### GET `/api/fabric/report-full-project`
Comprehensive project health and status report in JSON.

### GET `/api/fabric/reports/:type`
- **Params**: `type` (activity, diplomes, institutions, security)
- **Query**: `format=json|pdf`

---

## 🏛️ Microservices (Proxied)
Managed via `/discovery` endpoint:
- `POST /api/users/auth/login`
- `POST /api/institutions/`
- `POST /api/students/`
- `POST /api/pdf/generate-diploma`
