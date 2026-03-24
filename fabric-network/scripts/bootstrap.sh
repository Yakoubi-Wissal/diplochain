#!/bin/bash
# =============================================================================
# DiploChain — scripts/bootstrap.sh
# Initialise le réseau Hyperledger Fabric complet
# Usage : ./scripts/bootstrap.sh
# Prérequis : fabric-samples binaries dans $PATH ou ./bin/
# =============================================================================

set -e

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}   $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Répertoire racine du script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

# Charger les variables d'environnement
source .env

# Chercher les binaires Fabric (bin/ local ou PATH)
if [ -d "./bin" ]; then
  export PATH="$ROOT_DIR/bin:$PATH"
fi

# Vérification des outils requis
check_tools() {
  log_info "Vérification des outils requis..."
  for tool in cryptogen configtxgen docker docker-compose; do
    if ! command -v "$tool" &>/dev/null; then
      log_error "$tool introuvable. Installez les binaires Fabric 2.5 :\n  curl -sSL https://bit.ly/2ysbOFE | bash -s -- 2.5.9 1.5.12"
    fi
    log_ok "$tool trouvé : $(command -v $tool)"
  done
}

# Nettoyage de l'état précédent
cleanup() {
  log_warn "Nettoyage des artefacts précédents..."
  docker-compose -f docker-compose.fabric.yml down --volumes --remove-orphans 2>/dev/null || true
  rm -rf ./crypto-config ./channel-artifacts
  mkdir -p ./channel-artifacts
  log_ok "Nettoyage terminé"
}

# Génération des certificats cryptographiques
generate_crypto() {
  log_info "Génération des certificats (cryptogen)..."
  cryptogen generate --config=./crypto-config.yaml --output=./crypto-config
  log_ok "Crypto-config générée dans ./crypto-config/"
}

# Génération du genesis block (système orderer Raft)
generate_genesis() {
  log_info "Génération du genesis block..."
  export FABRIC_CFG_PATH="$ROOT_DIR"

  configtxgen \
    -profile DiploChainGenesis \
    -channelID diplochain-system-channel \
    -outputBlock ./channel-artifacts/genesis.block

  log_ok "Genesis block → ./channel-artifacts/genesis.block"
}

# Démarrage des conteneurs Docker
start_network() {
  log_info "Démarrage des conteneurs Fabric..."
  docker-compose -f docker-compose.fabric.yml up -d

  log_info "Attente de la disponibilité des services (15s)..."
  sleep 15

  # Vérification santé des conteneurs
  for svc in orderer.diplochain.local peer0.diplochain.local couchdb0.diplochain.local; do
    if docker ps --filter "name=$svc" --filter "status=running" | grep -q "$svc"; then
      log_ok "$svc → running"
    else
      log_error "$svc n'a pas démarré. Vérifiez : docker logs $svc"
    fi
  done
}

# Rejoindre l'orderer via osnadmin (Fabric 2.5 channel participation API)
join_orderer_to_system() {
  log_info "Enregistrement de l'orderer dans le système Raft..."
  # Avec Fabric 2.5+, pas de système channel — l'orderer attend les canaux applicatifs
  log_ok "Orderer prêt (mode channel participation)"
}

# Création du canal système DiploChain (canal de base, hors institutions)
# Les canaux par institution sont créés via create-channel.sh
create_system_channel() {
  log_info "Canal système ignoré (Fabric 2.5 channel participation — pas de genesis channel requis)"
  log_ok "Réseau prêt pour la création dynamique des canaux institution"
}

# =============================================================================
# Main
# =============================================================================
main() {
  echo ""
  echo "╔══════════════════════════════════════════════════════════╗"
  echo "║     DiploChain — Bootstrap Hyperledger Fabric 2.5        ║"
  echo "╚══════════════════════════════════════════════════════════╝"
  echo ""

  check_tools
  cleanup
  generate_crypto
  generate_genesis
  start_network
  join_orderer_to_system
  create_system_channel

  echo ""
  echo "╔══════════════════════════════════════════════════════════╗"
  echo "║  Réseau Fabric opérationnel !                            ║"
  echo "║  Prochaine étape : ./scripts/create-channel.sh <id>     ║"
  echo "║  Exemple : ./scripts/create-channel.sh 1                ║"
  echo "╚══════════════════════════════════════════════════════════╝"
  echo ""
}

main "$@"
