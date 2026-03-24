#!/bin/bash
# =============================================================================
# DiploChain — scripts/create-channel.sh
# Crée un canal Fabric dédié à une institution
# Appelé par institution-service lors de l'enregistrement d'une institution
#
# Usage : ./scripts/create-channel.sh <institution_id>
# Exemple : ./scripts/create-channel.sh 42
#   → crée le canal "channel_42" et y déploie le chaincode diplochain
#   → met à jour institution_blockchain_ext.channel_id = 'channel-42'
#
# Correspond exactement à : institution_blockchain_ext.channel_id (UNIQUE)
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}   $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Vérification argument
if [ -z "$1" ]; then
  log_error "Usage: $0 <institution_id>\n  Exemple: $0 42  (crée channel_42)"
fi

INSTITUTION_ID="$1"
CHANNEL_ID="channel-${INSTITUTION_ID}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

source .env

if [ -d "./bin" ]; then
  export PATH="$ROOT_DIR/bin:$PATH"
fi

export FABRIC_CFG_PATH="$ROOT_DIR"
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID=DiploChainOrgMSP
export CORE_PEER_TLS_ROOTCERT_FILE="$ROOT_DIR/crypto-config/peerOrganizations/diplochain.local/peers/peer0.diplochain.local/tls/ca.crt"
export CORE_PEER_MSPCONFIGPATH="$ROOT_DIR/crypto-config/peerOrganizations/diplochain.local/users/Admin@diplochain.local/msp"
export CORE_PEER_ADDRESS=peer0.diplochain.local:7051

ORDERER_CA="$ROOT_DIR/crypto-config/ordererOrganizations/orderer.diplochain.local/orderers/orderer.orderer.diplochain.local/tls/ca.crt"
ORDERER_ADMIN_TLS_SIGN_CERT="$ROOT_DIR/crypto-config/ordererOrganizations/orderer.diplochain.local/users/Admin@orderer.diplochain.local/tls/client.crt"
ORDERER_ADMIN_TLS_PRIVATE_KEY="$ROOT_DIR/crypto-config/ordererOrganizations/orderer.diplochain.local/users/Admin@orderer.diplochain.local/tls/client.key"

# =============================================================================
# Étape 1 : Générer le bloc de configuration du canal
# =============================================================================
generate_channel_config() {
  log_info "Génération du bloc de configuration pour $CHANNEL_ID..."

  configtxgen \
    -profile InstitutionChannel \
    -outputCreateChannelTx "./channel-artifacts/${CHANNEL_ID}.tx" \
    -channelID "$CHANNEL_ID"

  log_ok "Config tx → ./channel-artifacts/${CHANNEL_ID}.tx"
}

# =============================================================================
# Étape 2 : Créer le canal via osnadmin (Fabric 2.5)
# =============================================================================
create_channel() {
  log_info "Création du canal $CHANNEL_ID sur l'orderer..."

  # Générer le bloc genesis du canal
  configtxgen \
    -profile InstitutionChannel \
    -outputBlock "./channel-artifacts/${CHANNEL_ID}_genesis.block" \
    -channelID "$CHANNEL_ID"

  # Joindre l'orderer au canal via osnadmin
  osnadmin channel join \
    --channelID "$CHANNEL_ID" \
    --config-block "./channel-artifacts/${CHANNEL_ID}_genesis.block" \
    -o orderer.diplochain.local:7053 \
    --ca-file "$ORDERER_CA" \
    --client-cert "$ORDERER_ADMIN_TLS_SIGN_CERT" \
    --client-key "$ORDERER_ADMIN_TLS_PRIVATE_KEY"

  log_ok "Canal $CHANNEL_ID créé sur l'orderer"
  log_info "Attente activation canal (5s)..."
  sleep 5
}

# =============================================================================
# Étape 3 : Faire rejoindre le peer au canal
# =============================================================================
join_peer_to_channel() {
  log_info "Copie du cert orderer dans le conteneur peer..."

  docker cp \
    ./crypto-config/ordererOrganizations/orderer.diplochain.local/orderers/orderer.orderer.diplochain.local/tls/ca.crt \
    peer0.diplochain.local:/tmp/orderer-ca.crt

  docker cp \
    ./crypto-config/peerOrganizations/diplochain.local/users/Admin@diplochain.local/msp \
    peer0.diplochain.local:/tmp/admin-msp

  log_info "Récupération du bloc genesis du canal $CHANNEL_ID..."
  docker exec \
    -e CORE_PEER_MSPCONFIGPATH=/tmp/admin-msp \
    peer0.diplochain.local \
    peer channel fetch oldest "/tmp/${CHANNEL_ID}_config.block" \
    -c "$CHANNEL_ID" \
    -o orderer.diplochain.local:7050 \
    --tls --cafile /tmp/orderer-ca.crt

  log_info "Peer rejoignant le canal $CHANNEL_ID..."
  docker exec \
    -e CORE_PEER_MSPCONFIGPATH=/tmp/admin-msp \
    peer0.diplochain.local \
    peer channel join -b "/tmp/${CHANNEL_ID}_config.block"

  log_ok "peer0.diplochain.local a rejoint $CHANNEL_ID"
}
# =============================================================================
# Étape 4 : Mettre à jour les anchor peers
# =============================================================================
update_anchor_peers() {
  log_info "Mise à jour des anchor peers pour $CHANNEL_ID..."

  configtxgen \
    -profile InstitutionChannel \
    -outputAnchorPeersUpdate "./channel-artifacts/${CHANNEL_ID}_anchors.tx" \
    -channelID "$CHANNEL_ID" \
    -asOrg DiploChainOrgMSP

  peer channel update \
    -o orderer.diplochain.local:7050 \
    -c "$CHANNEL_ID" \
    -f "./channel-artifacts/${CHANNEL_ID}_anchors.tx" \
    --tls --cafile "$ORDERER_CA"

  log_ok "Anchor peers mis à jour pour $CHANNEL_ID"
}

# =============================================================================
# Étape 5 : Déployer le chaincode sur ce canal
# =============================================================================
deploy_chaincode() {
  log_info "Déploiement du chaincode $CHAINCODE_NAME sur $CHANNEL_ID..."

  PACKAGE_FILE="./channel-artifacts/${CHAINCODE_NAME}.tar.gz"

  # Package (une seule fois si déjà fait)
  if [ ! -f "$PACKAGE_FILE" ]; then
    log_info "Package du chaincode..."
    peer lifecycle chaincode package "$PACKAGE_FILE" \
      --path "$CHAINCODE_PATH" \
      --lang "$CHAINCODE_LANG" \
      --label "${CHAINCODE_NAME}_${CHAINCODE_VERSION}"
    log_ok "Package → $PACKAGE_FILE"
  fi

  # Install
  peer lifecycle chaincode install "$PACKAGE_FILE"

  # Récupérer le package ID
  PKG_ID=$(peer lifecycle chaincode queryinstalled 2>&1 \
    | grep "${CHAINCODE_NAME}_${CHAINCODE_VERSION}" \
    | awk -F'[, ]+' '{print $3}')

  log_info "Package ID : $PKG_ID"

  # Approve
  peer lifecycle chaincode approveformyorg \
    -o orderer.diplochain.local:7050 \
    --tls --cafile "$ORDERER_CA" \
    --channelID "$CHANNEL_ID" \
    --name "$CHAINCODE_NAME" \
    --version "$CHAINCODE_VERSION" \
    --package-id "$PKG_ID" \
    --sequence "$CHAINCODE_SEQUENCE"

  # Commit
  peer lifecycle chaincode commit \
    -o orderer.diplochain.local:7050 \
    --tls --cafile "$ORDERER_CA" \
    --channelID "$CHANNEL_ID" \
    --name "$CHAINCODE_NAME" \
    --version "$CHAINCODE_VERSION" \
    --sequence "$CHAINCODE_SEQUENCE" \
    --peerAddresses peer0.diplochain.local:7051 \
    --tlsRootCertFiles "$CORE_PEER_TLS_ROOTCERT_FILE"

  log_ok "Chaincode $CHAINCODE_NAME déployé sur $CHANNEL_ID"
}

# =============================================================================
# Étape 6 : Vérification finale + affichage infos pour institution-service
# =============================================================================
verify_and_print_info() {
  log_info "Vérification du canal $CHANNEL_ID..."

  peer channel list | grep -q "$CHANNEL_ID" && \
    log_ok "Canal $CHANNEL_ID visible dans peer channel list" || \
    log_warn "Canal $CHANNEL_ID non trouvé dans peer channel list"

  echo ""
  echo "╔══════════════════════════════════════════════════════════════════╗"
  echo "║  Canal créé avec succès !                                        ║"
  echo "╠══════════════════════════════════════════════════════════════════╣"
  printf "║  %-64s║\n" "institution_id   : $INSTITUTION_ID"
  printf "║  %-64s║\n" "channel_id       : $CHANNEL_ID"
  printf "║  %-64s║\n" "peer_node_url    : grpc://peer0.diplochain.local:7051"
  printf "║  %-64s║\n" "chaincode        : $CHAINCODE_NAME v$CHAINCODE_VERSION"
  echo "╠══════════════════════════════════════════════════════════════════╣"
  echo "║  À insérer dans PostgreSQL (institution-service) :               ║"
  echo "║  UPDATE institution_blockchain_ext                               ║"
  printf "║  %-64s║\n" "  SET channel_id = '$CHANNEL_ID',"
  echo "║      peer_node_url = 'grpc://peer0.diplochain.local:7051'        ║"
  printf "║  %-64s║\n" "  WHERE institution_id = $INSTITUTION_ID;"
  echo "╚══════════════════════════════════════════════════════════════════╝"
}

# =============================================================================
# Main
# =============================================================================
main() {
  echo ""
  echo "╔══════════════════════════════════════════════════════════════════╗"
  echo "║   DiploChain — Création canal institution $INSTITUTION_ID"
  echo "║   Canal : $CHANNEL_ID"
  echo "╚══════════════════════════════════════════════════════════════════╝"
  echo ""

  generate_channel_config
  create_channel
  join_peer_to_channel
  update_anchor_peers
  deploy_chaincode
  verify_and_print_info
}

main "$@"
