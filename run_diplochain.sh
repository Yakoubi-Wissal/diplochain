#!/bin/bash
# run_diplochain.sh — Start the complete DiploChain Audit System

echo "--- Starting DiploChain System (Unified) ---"

# 1. Start the entire stack
echo "Deploying Containers (Blockchain, Microservices, UI)..."
docker-compose up -d --build

echo "-----------------------------------"
echo "System launch complete."
echo "Audit Dashboard: http://localhost:3000"
echo "Fabric API:      http://localhost:4001"
echo "API Gateway:     http://localhost:8000"
echo "-----------------------------------"
echo "Tip: Run 'docker-compose logs -f' to see real-time output."
