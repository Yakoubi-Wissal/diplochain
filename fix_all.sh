#!/bin/bash
# fix_all.sh — Deploy/upgrade diplochain chaincode on channel-1
# Automatically detects the correct sequence number and package ID

set -e  # exit on error

# ── Navigate to fabric-network ──────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/fabric-network"

# ── Environment ─────────────────────────────────────────────────────────────
export PATH=$PWD/bin:$PATH
export FABRIC_CFG_PATH=$PWD
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID=DiploChainOrgMSP
export CORE_PEER_TLS_ROOTCERT_FILE="$PWD/crypto-config/peerOrganizations/diplochain.local/peers/peer0.diplochain.local/tls/ca.crt"
export CORE_PEER_MSPCONFIGPATH="$PWD/crypto-config/peerOrganizations/diplochain.local/users/Admin@diplochain.local/msp"
export CORE_PEER_ADDRESS=localhost:7051
ORDERER_CA="$PWD/crypto-config/ordererOrganizations/orderer.diplochain.local/orderers/orderer.orderer.diplochain.local/tls/ca.crt"

CHAINCODE_VERSION="${CHAINCODE_VERSION:-1.3}"
CHAINCODE_NAME="diplochain"
CHANNEL="channel-1"
CC_PACKAGE="./channel-artifacts/${CHAINCODE_NAME}_${CHAINCODE_VERSION}.tar.gz"

# ── Step 1: Auto-detect the correct next sequence number ───────────────────
echo "🔍 Querying committed chaincode sequence on $CHANNEL..."
COMMITTED_SEQ=$(peer lifecycle chaincode querycommitted \
  --channelID "$CHANNEL" --name "$CHAINCODE_NAME" \
  --output json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('sequence',0))" 2>/dev/null || echo "0")

CHAINCODE_SEQUENCE=$((COMMITTED_SEQ + 1))
echo "   Committed sequence : $COMMITTED_SEQ"
echo "   Next sequence      : $CHAINCODE_SEQUENCE"

# ── Step 2: Pull required Fabric Docker images if missing ──────────────────
echo ""
echo "🐳 Checking required Docker images..."
FABRIC_VERSION="2.5"
for IMG in "hyperledger/fabric-ccenv:${FABRIC_VERSION}" "hyperledger/fabric-baseos:${FABRIC_VERSION}"; do
  if ! docker image inspect "$IMG" &>/dev/null; then
    echo "   Pulling $IMG ..."
    docker pull "$IMG"
  else
    echo "   ✔ $IMG already present"
  fi
done

# ── Step 3: Package chaincode ───────────────────────────────────────────────
mkdir -p ./channel-artifacts
echo ""
echo "📦 Packaging chaincode v${CHAINCODE_VERSION}..."
peer lifecycle chaincode package "$CC_PACKAGE" \
  --path ./chaincode/diplochain --lang golang \
  --label "${CHAINCODE_NAME}_${CHAINCODE_VERSION}"

# ── Step 3: Install chaincode ───────────────────────────────────────────────
echo ""
echo "⬆️  Installing chaincode..."
peer lifecycle chaincode install "$CC_PACKAGE"

# ── Step 4: Auto-detect Package ID ─────────────────────────────────────────
echo ""
echo "🔍 Querying installed package ID..."
PKG_ID=$(peer lifecycle chaincode queryinstalled 2>&1 \
  | grep "${CHAINCODE_NAME}_${CHAINCODE_VERSION}" \
  | sed -n 's/.*Package ID: \([^,]*\),.*/\1/p' \
  | head -1)

if [ -z "$PKG_ID" ]; then
  echo "❌ ERROR: Could not find Package ID for ${CHAINCODE_NAME}_${CHAINCODE_VERSION}"
  echo "   Output of queryinstalled:"
  peer lifecycle chaincode queryinstalled 2>&1
  exit 1
fi
echo "   PKG_ID = $PKG_ID"

# ── Step 5: Approve ─────────────────────────────────────────────────────────
echo ""
echo "✅ Approving chaincode (sequence=$CHAINCODE_SEQUENCE)..."
peer lifecycle chaincode approveformyorg \
  -o orderer.diplochain.local:7050 --tls --cafile "$ORDERER_CA" \
  --channelID "$CHANNEL" --name "$CHAINCODE_NAME" \
  --version "$CHAINCODE_VERSION" \
  --package-id "$PKG_ID" \
  --sequence "$CHAINCODE_SEQUENCE"

# ── Step 6: Check readiness ─────────────────────────────────────────────────
echo ""
echo "🔎 Checking commit readiness..."
peer lifecycle chaincode checkcommitreadiness \
  -o orderer.diplochain.local:7050 --tls --cafile "$ORDERER_CA" \
  --channelID "$CHANNEL" --name "$CHAINCODE_NAME" \
  --version "$CHAINCODE_VERSION" \
  --sequence "$CHAINCODE_SEQUENCE" \
  --output json

# ── Step 7: Commit ──────────────────────────────────────────────────────────
echo ""
echo "🚀 Committing chaincode (sequence=$CHAINCODE_SEQUENCE)..."
peer lifecycle chaincode commit \
  -o orderer.diplochain.local:7050 --tls --cafile "$ORDERER_CA" \
  --channelID "$CHANNEL" --name "$CHAINCODE_NAME" \
  --version "$CHAINCODE_VERSION" \
  --sequence "$CHAINCODE_SEQUENCE" \
  --peerAddresses peer0.diplochain.local:7051 \
  --tlsRootCertFiles "$CORE_PEER_TLS_ROOTCERT_FILE"

# ── Done ────────────────────────────────────────────────────────────────────
echo ""
echo "🎉 Chaincode '${CHAINCODE_NAME}' v${CHAINCODE_VERSION} committed at sequence ${CHAINCODE_SEQUENCE} on ${CHANNEL}"
