#!/bin/bash
# fix_all.sh

cd fabric-network
export PATH=$PWD/bin:$PATH
export FABRIC_CFG_PATH=$PWD
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID=DiploChainOrgMSP
export CORE_PEER_TLS_ROOTCERT_FILE="$PWD/crypto-config/peerOrganizations/diplochain.local/peers/peer0.diplochain.local/tls/ca.crt"
export CORE_PEER_MSPCONFIGPATH="$PWD/crypto-config/peerOrganizations/diplochain.local/users/Admin@diplochain.local/msp"
export CORE_PEER_ADDRESS=localhost:7051
ORDERER_CA="$PWD/crypto-config/ordererOrganizations/orderer.diplochain.local/orderers/orderer.orderer.diplochain.local/tls/ca.crt"

echo "Packaging chaincode v1.3..."
peer lifecycle chaincode package ./channel-artifacts/diplochain_1.3.tar.gz \
  --path ./chaincode/diplochain --lang golang --label diplochain_1.3

echo "Installing chaincode v1.3..."
peer lifecycle chaincode install ./channel-artifacts/diplochain_1.3.tar.gz

echo "Getting Package ID..."
PKG_ID=$(peer lifecycle chaincode queryinstalled | grep "diplochain_1.3" | awk -F'[, ]+' '{print $3}')
echo "PKG_ID=$PKG_ID"

echo "Approving for channel-1..."
peer lifecycle chaincode approveformyorg -o localhost:7050 --tls --cafile "$ORDERER_CA" \
  --channelID channel-1 --name diplochain --version 1.3 --package-id "$PKG_ID" --sequence 4

echo "Committing to channel-1..."
peer lifecycle chaincode commit -o localhost:7050 --tls --cafile "$ORDERER_CA" \
  --channelID channel-1 --name diplochain --version 1.3 --sequence 4 \
  --peerAddresses localhost:7051 --tlsRootCertFiles "$CORE_PEER_TLS_ROOTCERT_FILE"

echo "Done!"
