#!/usr/bin/env bash
# Bi0cyph3r — start Arcium MPC service (uses Solana CLI keypair)
# Run from biocypher-mxe so Arcium config is found.
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MXE_DIR="$REPO_ROOT/biocypher-mxe"
SERVICE_DIR="$REPO_ROOT/biocypher-arcium-service"

if [[ ! -d "$SERVICE_DIR" ]]; then
  echo "Error: biocypher-arcium-service not found"
  exit 1
fi

cd "$SERVICE_DIR"
if [[ ! -d node_modules ]]; then
  echo "Installing dependencies..."
  npm install
fi

if [[ ! -d dist ]]; then
  echo "Building..."
  npm run build
fi

echo "🧬 Starting Arcium service (run from biocypher-mxe context)..."
echo "   MXE_PATH=$MXE_DIR"
echo "   Start Arcium localnet first: cd biocypher-mxe && arcium test (or arcium localnet)"
echo ""

cd "$MXE_DIR"
MXE_PATH="$MXE_DIR" node "$SERVICE_DIR/dist/index.js"
