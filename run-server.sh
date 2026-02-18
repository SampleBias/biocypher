#!/usr/bin/env bash
# Bi0cyph3r — start API server + Web UI
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT/biocypher-rust-solana"

echo "🧬 Starting Bi0cyph3r server..."
echo ""
echo "  API:     http://127.0.0.1:8080"
echo "  Web UI:  http://127.0.0.1:8080/app/"
echo ""
cargo run --bin biocypher-backend
