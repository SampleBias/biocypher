# BioCypher

**DNA Cryptography System** — Encode and decode messages as DNA sequences with optional blockchain verification.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## Overview

BioCypher is a DNA-based encoding system for storing and transmitting digital data. It supports three encoding modes optimized for different use cases:

| Mode | Description | Use Case |
|------|-------------|----------|
| **Basic** | Simple binary→DNA mapping (00=A, 01=T, 10=C, 11=G) | Educational, simple encoding |
| **Nanopore** | Triplet encoding, error correction, GC balancing, homopolymer avoidance | Nanopore sequencing optimization |
| **Secure** | AES-256-CBC encryption + DNA encoding | Secure data storage |

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
| **Solana Programs** | ⏳ Planned (Phase 2) |
| **Solana Integration** | ⏳ Planned (Phase 3) |

---

## Quick Start

### Prerequisites

- [Rust](https://rustup.rs/) (1.70+)
- (Optional) [Solana CLI](https://docs.solana.com/cli/install-solana-cli-tools) for Phase 2+

### Run the Backend

```bash
cd biocypher-rust-solana
cargo run
```

Server starts at **http://127.0.0.1:8080**

### API Examples

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

---

## Project Structure

```
biocypher/
├── biocypher-rust-solana/     # Rust backend (Actix-web)
│   ├── backend/
│   │   └── src/
│   │       ├── api/           # HTTP endpoints (encode, decode, safety)
│   │       ├── dna/           # Basic, Nanopore, Secure crypto
│   │       ├── safety/        # Pathogen & sequence screening
│   │       └── main.rs
│   └── Cargo.toml
├── biocypher/                 # Python reference implementation
│   ├── dna_crypto.py
│   ├── nanopore_dna_crypto.py
│   ├── secure_nanopore_dna_crypto.py
│   ├── safety_screener.py
│   └── PROTOCOL_SPECIFICATION.md
├── docs/                      # Documentation
├── tasks/                     # Implementation plans
├── BUILD_PLAN.md              # Phased build plan
├── LICENSE                    # MIT License
└── README.md
```

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

### Rust Backend (Implemented)

- **actix-web** 4.4 — Web framework
- **tokio** 1.35 — Async runtime
- **aes** + **cbc** — AES-256-CBC encryption (Secure mode)
- **pbkdf2** — Key derivation (100,000 iterations)
- **base64** — Crypto data serialization
- **regex** — Pattern matching (safety screener)

### Planned (Phase 2–3)

- **Solana** — Blockchain programs (Encoder, Decoder, Safety)
- **Anchor** — Solana program framework

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

## Testing

```bash
cd biocypher-rust-solana
cargo test
```

50+ unit tests cover Basic, Nanopore, Secure modes and the safety screener.

---

## Roadmap

| Phase | Focus | Status |
|-------|-------|--------|
| **1** | Rust backend (all 3 DNA modes) | ✅ Complete |
| **2** | Solana smart programs | ⏳ Planned |
| **3** | Backend–Solana integration | ⏳ Planned |
| **4** | Frontend updates | ⏳ Planned |
| **5** | Testing & hardening | ⏳ Planned |
| **6** | Deployment | ⏳ Planned |

See [BUILD_PLAN.md](BUILD_PLAN.md) for details.

---

## Documentation

- [BUILD_PLAN.md](BUILD_PLAN.md) — Phased implementation plan
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

**BioCypher** — DNA cryptography for the modern stack.
