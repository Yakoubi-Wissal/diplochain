#!/bin/bash
# =============================================================================
# DiploChain — scripts/install-fabric.sh
# Télécharge les binaires Hyperledger Fabric 2.5 et les images Docker
# Usage : ./scripts/install-fabric.sh
# =============================================================================

set -e

FABRIC_VERSION="2.5.9"
FABRIC_CA_VERSION="1.5.12"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  DiploChain — Installation Hyperledger Fabric $FABRIC_VERSION   ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Téléchargement via script officiel Hyperledger
# -d = Docker images, -b = binaires, -s = fabric-samples (ignorés)
curl -sSL https://bit.ly/2ysbOFE | bash -s -- \
  "$FABRIC_VERSION" \
  "$FABRIC_CA_VERSION" \
  -d -b

# Déplacer les binaires dans ./bin/
if [ -d "./fabric-samples/bin" ]; then
  mv ./fabric-samples/bin ./bin
  rm -rf ./fabric-samples
  echo ""
  echo "[OK] Binaires installés dans $ROOT_DIR/bin/"
  echo "[OK] Images Docker Fabric $FABRIC_VERSION téléchargées"
fi

# Vérification
echo ""
echo "Binaires disponibles :"
for bin in cryptogen configtxgen configtxlator osnadmin peer orderer; do
  if [ -f "./bin/$bin" ]; then
    echo "  [OK] ./bin/$bin"
  else
    echo "  [WARN] ./bin/$bin manquant"
  fi
done

echo ""
echo "Go requis pour le chaincode. Vérification :"
if command -v go &>/dev/null; then
  echo "  [OK] Go $(go version)"
else
  echo "  [WARN] Go non trouvé. Installer : https://go.dev/dl/"
  echo "         Puis : go mod download (dans chaincode/diplochain/)"
fi

echo ""
echo "[OK] Installation terminée. Prochaine étape : ./scripts/bootstrap.sh"
