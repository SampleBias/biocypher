#!/usr/bin/env bash
# Bi0cyph3r install script — build and optionally install the CLI binary
# Usage: ./install.sh [ -i ]   ( -i = install to ~/.local/bin )
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT/biocypher-rust-solana"

echo "🧬 Building Bi0cyph3r..."
cargo build --release --bin bi0cyph3r

BIN="$REPO_ROOT/biocypher-rust-solana/target/release/bi0cyph3r"
echo ""
echo "✅ Build complete!"
echo ""
echo "  CLI:  $BIN"
echo "  Server: ./run-server.sh"

if [[ "$1" == "-i" ]]; then
  INSTALL_DIR="$HOME/.local/bin"
  mkdir -p "$INSTALL_DIR"
  cp "$BIN" "$INSTALL_DIR/bi0cyph3r"
  chmod +x "$INSTALL_DIR/bi0cyph3r"
  echo ""
  echo "  Installed to $INSTALL_DIR/bi0cyph3r"
  echo "  (ensure $INSTALL_DIR is in your PATH)"
fi

echo ""
echo "Usage:"
echo "  bi0cyph3r encode \"Hello World\""
echo "  bi0cyph3r decode \"TACATCTTTCG...\""
echo "  bi0cyph3r safety \"ATCGATCG\""
echo ""
echo "  ./run-server.sh   # Start API + Web UI"
