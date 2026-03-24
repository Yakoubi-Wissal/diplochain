#!/bin/bash
# redeploy_chaincode.sh — Upgrade chaincode on a specific channel

if [ -z "$1" ]; then
  echo "Usage: $0 <channel_id>"
  exit 1
fi

CHANNEL_ID=$1
# Determine current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Fix: Ensure we are in the root of the project to find fabric-network
if [[ "$SCRIPT_DIR" == *"fabric-network"* ]]; then
  BASE_DIR="$(dirname "$SCRIPT_DIR")"
else
  BASE_DIR="$SCRIPT_DIR"
fi

cd "$BASE_DIR/fabric-network"
echo "Working in $PWD"

if [ ! -f ".env" ]; then
  echo "Error: .env not found in $PWD"
  exit 1
fi

source .env

# Export paths and vars (using absolute paths)
export PATH="$PWD/bin:$PATH"
export FABRIC_CFG_PATH="$PWD"
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID=DiploChainOrgMSP
export CORE_PEER_TLS_ROOTCERT_FILE="$PWD/crypto-config/peerOrganizations/diplochain.local/peers/peer0.diplochain.local/tls/ca.crt"
export CORE_PEER_MSPCONFIGPATH="$PWD/crypto-config/peerOrganizations/diplochain.local/users/Admin@diplochain.local/msp"
export CORE_PEER_ADDRESS=peer0.diplochain.local:7051
ORDERER_CA="$PWD/crypto-config/ordererOrganizations/orderer.diplochain.local/orderers/orderer.orderer.diplochain.local/tls/ca.crt"

echo "Updating chaincode to v1.3 on $CHANNEL_ID..."

# Package
PACKAGE_FILE="./channel-artifacts/${CHAINCODE_NAME}_v1.3.tar.gz"
peer lifecycle chaincode package "$PACKAGE_FILE" \
  --path "$CHAINCODE_PATH" \
  --lang "$CHAINCODE_LANG" \
  --label "${CHAINCODE_NAME}_1.3"

# Install
peer lifecycle chaincode install "$PACKAGE_FILE"

# Get PKG_ID
PKG_ID=$(peer lifecycle chaincode queryinstalled | grep "${CHAINCODE_NAME}_1.3" | awk -F'[, ]+' '{print $3}')
if [ -z "$PKG_ID" ]; then
  echo "Error: Failed to get Package ID"
  exit 1
fi
echo "Package ID: $PKG_ID"

# Approve
peer lifecycle chaincode approveformyorg \
  -o orderer.diplochain.local:7050 --tls --cafile "$ORDERER_CA" \
  --channelID "$CHANNEL_ID" --name "$CHAINCODE_NAME" \
  --version "1.3" --package-id "$PKG_ID" --sequence 4

# Commit
peer lifecycle chaincode commit \
  -o orderer.diplochain.local:7050 --tls --cafile "$ORDERER_CA" \
  --channelID "$CHANNEL_ID" --name "$CHAINCODE_NAME" \
  --version "1.3" --sequence 4 \
  --peerAddresses peer0.diplochain.local:7051 \
  --tlsRootCertFiles "$CORE_PEER_TLS_ROOTCERT_FILE"

echo "Chaincode upgraded to 1.1 on $CHANNEL_ID"
