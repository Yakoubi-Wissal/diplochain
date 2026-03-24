#!/bin/bash
# run_diplochain.sh — Start the complete DiploChain Audit System

echo "--- Starting DiploChain System ---"

# 0. Start Base Infrastructure (Postgres, IPFS, etc.)
echo "Starting Base Infrastructure..."
docker-compose up -d postgres ipfs-node
sleep 5

# 0b. Start Fabric Network
echo "Starting Hyperledger Fabric Network..."
cd fabric-network
docker-compose -f docker-compose.fabric.yml up -d
echo "Waiting for Fabric containers to be ready..."
sleep 10

# 0c. Upgrade Chaincode to v1.1 (fix metadata panic)
if [ -f "./redeploy_chaincode.sh" ]; then
  chmod +x ./redeploy_chaincode.sh
  ./redeploy_chaincode.sh channel-1
fi

cd ..
echo "Ensuring Backend dependencies..."
cd fabric-api-server
if [ ! -d "node_modules/node-fetch" ]; then
  npm install node-fetch@2
fi
echo "Starting Backend (fabric-api-server)..."
node index.js &
BACKEND_PID=$!
cd ..

# 2. Start Audit Dashboard (Frontend)
echo "Starting Frontend (audit-dashboard)..."
cd audit-dashboard
npm run dev &
FRONTEND_PID=$!
cd ..

echo "System components launched."
echo "Backend PID: $BACKEND_PID (http://localhost:4001)"
echo "Frontend PID: $FRONTEND_PID (check terminal for port, usually http://localhost:3000 or 5173)"
echo "-----------------------------------"

# Keep script running
wait
