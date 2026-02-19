# Bi0cyph3r

```
 .----------------.  .----------------.  .----------------.  .----------------.  .----------------.  .----------------.  .----------------.  .----------------.  .----------------. 
| .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. |
| |   ______     | || |     _____    | || |     ____     | || |     ______   | || |  ____  ____  | || |   ______     | || |  ____  ____  | || |    ______    | || |  _______     | |
| |  |_   _ \    | || |    |_   _|   | || |   .'    '.   | || |   .' ___  |  | || | |_  _||_  _| | || |  |_   __ \   | || | |_   ||   _| | || |   / ____ `.  | || | |_   __ \    | |
| |    | |_) |   | || |      | |     | || |  |  .--.  |  | || |  / .'   \_|  | || |   \ \  / /   | || |    | |__) |  | || |   | |__| |   | || |   `'  __) |  | || |   | |__) |   | |
| |    |  __'.   | || |      | |     | || |  | |    | |  | || |  | |         | || |    \ \/ /    | || |    |  ___/   | || |   |  __  |   | || |   _  |__ '.  | || |   |  __ /    | |
| |   _| |__) |  | || |     _| |_    | || |  |  `--'  |  | || |  \ `.___.'\  | || |    _|  |_    | || |   _| |_      | || |  _| |  | |_  | || |  | \____) |  | || |  _| |  \ \_  | |
| |  |_______/   | || |    |_____|   | || |   '.____.'   | || |   `._____.'  | || |   |______|   | || |  |_____|     | || | |____||____| | || |   \______.'  | || | |____| |___| | |
| |              | || |              | || |              | || |              | || |              | || |              | || |              | || |              | || |              | |
| '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' |
 '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------' 
                                                          
    DNA Cryptography + MPC Privacy on Solana
```

**DNA Cryptography System** — Encode and decode messages as DNA sequences with optional blockchain verification and **Arcium MPC** for confidential computation.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## Overview

Bi0cyph3r is a DNA-based encoding system for storing and transmitting digital data. It supports three encoding modes and **Arcium-powered MPC** for privacy-preserving computation:

| Mode | Description | Use Case |
|------|-------------|----------|
| **Basic** | Simple binary→DNA mapping (00=A, 01=T, 10=C, 11=G) | Educational, simple encoding |
| **Nanopore** | Triplet encoding, error correction, GC balancing, homopolymer avoidance | Nanopore sequencing optimization |
| **Secure** | AES-256-CBC encryption + DNA encoding | Secure data storage |
| **Arcium MPC** | Encrypted computation—message never decrypted on server | Confidential DNA encoding on Solana |

---

## Arcium: Super Encrypted Computing

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ARCIUM MPC ENCRYPTED DNA ENCODING                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Client                Solana / Arcium              MPC Cluster            │
│     │                          │                            │               │
│     │  1. Encrypt message      │                            │               │
│     │  2. Submit to MXE        │                            │               │
│     │ ────────────────────────>│  3. Queue computation      │               │
│     │                          │ ──────────────────────────>│               │
│     │                          │                            │ 4. Compute   │
│     │                          │                            │    in MPC     │
│     │                          │  5. Callback (encrypted)   │               │
│     │                          │<───────────────────────────│               │
│     │  6. Decrypt DNA result   │                            │               │
│     │<────────────────────────│                            │               │
│     │                          │                            │               │
│     └── Message & result stay encrypted end-to-end ────────────────────────┘
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Why Arcium?** Your message is encrypted before it leaves your device. The MPC cluster computes on secret-shared data—no single node ever sees plaintext. Only you can decrypt the DNA result.

---

## Project Status

| Component | Status |
|-----------|--------|
| **Rust Backend** | ✅ Complete (Phase 1) |
| **Basic DNA Mode** | ✅ Implemented |
| **Nanopore DNA Mode** | ✅ Implemented |
| **Secure DNA Mode** | ✅ Implemented |
| **Safety Screener** | ✅ Implemented |
| **REST API** | ✅ Working |
| **Arcium MXE** | ✅ Implemented (encode_basic, decode_basic) |
| **Arcium Integration** | ✅ Backend `/api/arcium-info` |
| **CLI** | ✅ `bi0cyph3r` encode/decode/safety |
| **Web UI** | ✅ Browser-based at `/app/` |
| **Solana Programs** | ⏳ Planned (Phase 2) |
| **Solana Integration** | ⏳ Planned (Phase 3) |

---

## Quick Start

### Prerequisites

- [Rust](https://rustup.rs/) (1.70+)
- (Optional) [Solana CLI](https://docs.solana.com/cli/install-solana-cli-tools)
- (Optional) [Arcium CLI](https://docs.arcium.com/developers/installation) for MXE

### Option 1: Install script (recommended)

```bash
./install.sh          # Build CLI
./install.sh -i       # Build + install to ~/.local/bin

# CLI usage
bi0cyph3r encode "Hello World"
bi0cyph3r decode "TACATCTTTCGATCGATCGG"
bi0cyph3r safety "ATCGATCGATCG"

# Start server + Web UI
./run-server.sh
```

### Option 2: Offline mode (no server, no network)

**Single HTML file** — Save and open anywhere. Basic encode/decode only. No data leaves your device.

```bash
# Save and open in a browser (file:// or served)
open biocypher-rust-solana/static/offline.html
# Or copy the file and open it on any machine
```

**CLI** — Fully offline for Basic mode:

```bash
cd biocypher-rust-solana
cargo build --release --bin bi0cyph3r

./target/release/bi0cyph3r encode "Hello World" --mode basic
./target/release/bi0cyph3r decode "TACATCTTTCGATCGATCGG" --mode basic
./target/release/bi0cyph3r safety "ATCGATCGATCG"
```

### Option 3: Web UI + API Server

```bash
./run-server.sh
# or: cd biocypher-rust-solana && cargo run
```

- **API**: http://127.0.0.1:8080
- **Web UI**: http://127.0.0.1:8080/app/

### Option 4: Arcium MPC (Secure Encryption)

Uses Solana CLI keypair — no Phantom wallet needed.

```bash
# 1. Build MXE (one-time)
cd biocypher-mxe
yarn install
arcium build

# 2. Start Arcium localnet (in one terminal)
arcium test   # or: arcium localnet

# 3. Start Arcium service (in another terminal)
./run-arcium-service.sh

# 4. Start backend + Web UI
./run-server.sh
```

Then open http://127.0.0.1:8080/app/ and toggle **Arcium MPC** on. When connected, encode/decode use MPC — message stays encrypted end-to-end.

**Limits**: Arcium encode max 4 chars, decode exactly 16 bases.

**Troubleshooting `arcium build` — edition2024 / Rust version:**

If you see `feature 'edition2024' is required` or `Failed to build Anchor program`, Arcium’s dependencies need Rust 1.85+. Do both:

1. **Upgrade Solana/Agave** to 3.1.x (platform-tools v1.52 with Rust 1.89):
   ```bash
   sh -c "$(curl -sSfL https://release.anza.xyz/v3.1.8/install)"
   export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
   ```

2. **Install Rust 1.89** for `cargo metadata` (host dependency resolution):
   ```bash
   rustup install 1.89.0
   ```
   The `biocypher-mxe/rust-toolchain.toml` file pins Rust 1.89 for this project.

Then run `arcium build` from `biocypher-mxe/`.

### Run the Arcium MXE (MPC Encrypted Encoding)

```bash
# Install Arcium (one-time)
curl --proto '=https' --tlsv1.2 -sSfL https://install.arcium.com/ | bash

# Build and test the MXE
cd biocypher-mxe
yarn install
arcium build
arcium test
```

---

## API Examples

**Encode (Basic mode):**
```bash
curl -X POST http://127.0.0.1:8080/api/encode \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello World","mode":"basic"}'
```

**Encode (Nanopore mode):**
```bash
curl -X POST http://127.0.0.1:8080/api/encode \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello World","mode":"nanopore"}'
```

**Encode (Secure mode — requires password):**
```bash
curl -X POST http://127.0.0.1:8080/api/encode \
  -H "Content-Type: application/json" \
  -d '{"message":"Secret","mode":"secure","password":"YourSecurePass123!"}'
```

**Decode:**
```bash
curl -X POST http://127.0.0.1:8080/api/decode \
  -H "Content-Type: application/json" \
  -d '{"sequence":"TACATCTTTCGATCGATCGG","mode":"basic"}'
```

**Safety Screen:**
```bash
curl -X POST http://127.0.0.1:8080/api/safety-screen \
  -H "Content-Type: application/json" \
  -d '{"dna_sequence":"ATCGATCGATCGATCG"}'
```

**Arcium MXE Info:**
```bash
curl http://127.0.0.1:8080/api/arcium-info
```

---

## Project Structure

```
biocypher/
├── biocypher-rust-solana/       # Rust backend (Actix-web)
│   ├── backend/
│   │   └── src/
│   │       ├── api/             # HTTP endpoints
│   │       ├── arcium/          # Arcium integration info
│   │       ├── dna/             # Basic, Nanopore, Secure crypto
│   │       ├── safety/          # Pathogen & sequence screening
│   │       └── main.rs
│   └── Cargo.toml
│
├── biocypher-mxe/               # Arcium MXE (MPC encrypted DNA)
│   ├── programs/
│   │   └── biocypher-mxe/       # Solana program + Arcium instructions
│   ├── encrypted-ixs/           # Arcis circuits (encode_basic, decode_basic)
│   ├── tests/                   # TypeScript tests
│   ├── Arcium.toml
│   └── Anchor.toml
│
├── biocypher-arcium-service/    # Node.js Arcium proxy (Solana CLI keypair)
│   ├── src/
│   │   ├── index.ts             # Express server
│   │   └── arcium-client.ts     # Arcium encode/decode
│   └── package.json
│
├── biocypher/                   # Python reference implementation
│   ├── dna_crypto.py
│   ├── nanopore_dna_crypto.py
│   ├── secure_nanopore_dna_crypto.py
│   ├── safety_screener.py
│   └── PROTOCOL_SPECIFICATION.md
│
├── docs/
│   ├── ARCIUM_EDUCATIONAL_GUIDE.md   # Arcium concepts & workflow
│   ├── QUICK_REFERENCE.md
│   └── SUMMARY.md
│
├── tasks/
├── BUILD_PLAN.md
├── LICENSE
└── README.md
```

---

## Arcium MXE Details

```
  ┌──────────────────────────────────────────────────────────────┐
  │  BI0CYPH3R MXE — MPC EXECUTION ENVIRONMENT                   │
  ├──────────────────────────────────────────────────────────────┤
  │                                                              │
  │  Confidential Instructions (Arcis):                           │
  │  • encode_basic  — 4 bytes → 16 DNA bases (0=A, 1=T, 2=C, 3=G)│
  │  • decode_basic — 16 DNA bases → 4 bytes                      │
  │                                                              │
  │  Crypto: Rescue cipher + x25519 ECDH                          │
  │  Trust:  Cerberus (dishonest majority)                        │
  │                                                              │
  └──────────────────────────────────────────────────────────────┘
```

| Instruction | Input | Output |
|-------------|-------|--------|
| `encode_basic` | 4 encrypted bytes | 16 encrypted DNA bases |
| `decode_basic` | 16 encrypted DNA bases | 4 encrypted bytes |

See [docs/ARCIUM_EDUCATIONAL_GUIDE.md](docs/ARCIUM_EDUCATIONAL_GUIDE.md) for full documentation.

---

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| POST | `/api/encode` | Encode message to DNA |
| POST | `/api/decode` | Decode DNA to message |
| POST | `/api/safety-screen` | Screen DNA sequence for safety |
| GET | `/api/arcium-info` | Arcium MXE integration info |

### Encode Request

```json
{
  "message": "Hello",
  "mode": "basic",
  "password": null,
  "store_on_chain": false
}
```

- `mode`: `"basic"` | `"nanopore"` | `"secure"`
- `password`: Required for `secure` mode
- `store_on_chain`: Reserved for Phase 3 (Solana)

### Encode Response

```json
{
  "dna_sequence": "TACATCTTTCGATCGATCGG",
  "transaction_signature": null,
  "stats": {
    "length": 20,
    "bases": {"a": 4, "t": 7, "c": 5, "g": 4},
    "gc_content": 45.0
  }
}
```

---

## Technology Stack

### Rust Backend

- **actix-web** 4.4 — Web framework
- **tokio** 1.35 — Async runtime
- **aes** + **cbc** — AES-256-CBC encryption (Secure mode)
- **pbkdf2** — Key derivation (100,000 iterations)
- **base64** — Crypto data serialization
- **regex** — Pattern matching (safety screener)

### Arcium MXE

- **Arcium** 0.8 — MPC encrypted computation
- **Arcis** — Rust DSL for confidential instructions
- **Anchor** 0.32 — Solana program framework
- **Solana** — Orchestration & verification

### Planned (Phase 2–3)

- **Solana** — On-chain Encoder, Decoder, Safety programs
- **Backend–Solana** — `store_on_chain`, `decode_on_chain`

---

## DNA Encoding Modes

### Basic Mode

- **Mapping**: 00→A, 01→T, 10→C, 11→G
- **Format**: Raw DNA, no markers
- **Speed**: ~10ms

### Nanopore Mode

- **Encoding**: 9-bit parity + triple redundancy + triplet encoding
- **Markers**: `ATCGATCG` (start) / `CGATATCG` (stop)
- **Features**: Error correction, homopolymer avoidance, GC balancing
- **Speed**: ~30ms

### Secure Mode

- **Encryption**: AES-256-CBC with PBKDF2 key derivation
- **Format**: Base64(ciphertext) encoded as DNA + markers
- **Markers**: Same as Nanopore
- **Speed**: ~20ms

---

## Safety Screener

The safety module analyzes DNA sequences for:

- **Pathogen signatures** — Viral polymerase, toxins, antibiotic resistance
- **Natural occurrence** — Housekeeping genes, E. coli, human genome matches
- **Sequence characteristics** — GC content, homopolymers, ORFs, repetitive elements
- **Risk assessment** — Safe / Caution / Unsafe

---

## Install (Release Binary)

```bash
./install.sh
# Or manually:
cd biocypher-rust-solana && cargo build --release --bin bi0cyph3r
cp target/release/bi0cyph3r ~/.local/bin/
```

## Testing

**Backend:**
```bash
cd biocypher-rust-solana
cargo test
```

**Arcium MXE:**
```bash
cd biocypher-mxe
arcium test
```

---

## Roadmap

| Phase | Focus | Status |
|-------|-------|--------|
| **1** | Rust backend (all 3 DNA modes) | ✅ Complete |
| **1.5** | Arcium MXE (MPC encode/decode) | ✅ Complete |
| **2** | Solana smart programs | ⏳ Planned |
| **3** | Backend–Solana integration | ⏳ Planned |
| **4** | Frontend updates | ⏳ Planned |
| **5** | Testing & hardening | ⏳ Planned |
| **6** | Deployment | ⏳ Planned |

See [BUILD_PLAN.md](BUILD_PLAN.md) for details.

---

## Documentation

- [BUILD_PLAN.md](BUILD_PLAN.md) — Phased implementation plan
- [docs/ARCIUM_EDUCATIONAL_GUIDE.md](docs/ARCIUM_EDUCATIONAL_GUIDE.md) — Arcium concepts, MPC lifecycle, Arcis
- [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) — Developer quick reference
- [docs/SUMMARY.md](docs/SUMMARY.md) — Executive summary
- [biocypher/PROTOCOL_SPECIFICATION.md](biocypher/PROTOCOL_SPECIFICATION.md) — Protocol spec

---

## License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

The Python reference implementation in `biocypher/` may have different licensing terms; see `biocypher/LICENSE`.

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

---

```
  ╔═══════════════════════════════════════════════════════════════╗
  ║  Bi0cyph3r — DNA cryptography for the modern stack             ║
  ║  Rust • Solana • Arcium MPC • Privacy by design                ║
  ╚═══════════════════════════════════════════════════════════════╝
```
