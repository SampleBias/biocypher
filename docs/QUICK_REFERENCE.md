# BioCypher Rust + Solana - Quick Reference Guide

## TL;DR

**Q: Can we build a Rust backend with Solana integration for BioCypher?**
**A: YES! Using hybrid architecture - Rust for fast operations, Solana for verifiable storage.**

---

## Architecture at a Glance

```
UI (React)
  ↓ HTTP
Rust Backend (Actix-web)
  ├─→ Fast operations (off-chain, FREE, 10-50ms)
  └─→ Verifiable operations (on-chain, $0.00075, 400-800ms)
       ↓
      Solana Blockchain
```

---

## Key Commands

### Development Setup
```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install Solana CLI
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"

# Install Anchor Framework
cargo install --git https://github.com/coral-xyz/anchor avm --locked --force
avm install latest
avm use latest

# Start local validator
solana-test-validator

# Start Rust backend (from backend/)
cargo run

# Start frontend (from frontend/)
npm install && npm start
```

### Build & Test
```bash
# Build Rust backend
cargo build --release

# Run tests
cargo test

# Build Solana programs
anchor build

# Deploy to devnet
anchor deploy --provider.cluster devnet

# Run program tests
anchor test
```

---

## Project Structure (Quick View)

```
biocypher-rust-solana/
├── backend/              # Rust API server
│   ├── src/
│   │   ├── dna/         # DNA crypto (basic, nanopore, secure)
│   │   ├── safety/      # Safety screener
│   │   ├── solana/      # Solana client wrapper
│   │   └── api/         # HTTP endpoints
│   └── Cargo.toml
│
├── programs/            # Solana smart programs
│   ├── biocypher-encoder/
│   ├── biocypher-decoder/
│   └── biocypher-safety/
│
└── frontend/            # React UI
    ├── src/
    │   ├── components/
    │   └── api/
    └── package.json
```

---

## API Endpoints

### Encoding
```
POST /api/encode
Body: {message, mode, password?, store_on_chain?}
Response: {dna_sequence, transaction_signature?, stats}

Example:
curl -X POST http://localhost:8080/api/encode \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello World","mode":"basic","store_on_chain":false}'
```

### Decoding
```
POST /api/decode
Body: {sequence, mode, password?, decode_on_chain?}
Response: {decoded_message, transaction_signature?, stats}
```

### Safety Screening
```
POST /api/safety-screen
Body: {dna_sequence, verify_on_chain?}
Response: {safety_status, pathogen_analysis, recommendations, transaction_signature?}
```

### Verification
```
GET /api/verify/:signature
Response: {transaction, dna_record, verified}
```

---

## DNA Encoding Modes

### Basic Mode
- **Mapping**: 00=A, 01=T, 10=C, 11=G
- **Speed**: Very fast (~10ms)
- **Output**: 4 bases per character
- **Use Case**: Simple encoding, educational

**Example:** "Hi" → TAAATATA → 32 bases

### Nanopore Mode
- **Encoding**: Triplet encoding (8 triplets)
- **Features**: Error correction, homopolymer avoidance, GC balancing
- **Speed**: Fast (~30ms)
- **Output**: ~35 bases per character (with markers)
- **Use Case:** Nanopore sequencing optimization

**Example:** "Hello" → ATCGATCG...CGATATCG → ~350 bases

### Secure Mode
- **Encryption**: AES-256-CBC
- **Key Derivation**: PBKDF2 (100,000 iterations)
- **Speed**: Fast (~20ms)
- **Output**: Varies (encrypted data + markers)
- **Use Case:** Secure data storage, sensitive messages

**Example:** "Secret" → ATCGATCG...CGATATCG → encrypted

---

## Solana Programs

### 1. Encoder Program
**Program ID:** `Bi0EnCoDeRxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**Instructions:**
- `encode_basic` - Simple encoding, store on-chain
- `encode_nanopore` - Nanopore encoding with EC, store on-chain
- `encode_secure` - AES encryption + DNA, store on-chain

**Account:** DNARecord (owner, mode, message, dna_sequence, timestamp)

### 2. Decoder Program
**Program ID:** `Bi0DeCoDeRxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**Instructions:**
- `decode_basic` - Decode basic DNA on-chain
- `decode_nanopore` - Decode nanopore DNA with EC on-chain
- `decode_secure` - Decrypt + decode on-chain

**Account:** DecodeResult (dna_sequence, decoded_message, timestamp)

### 3. Safety Program
**Program ID:** `Bi0S4FeTyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**Instructions:**
- `screen_sequence` - Screen DNA for safety on-chain

**Account:** SafetyReport (dna_sequence, safety_status, pathogen_risk, etc.)

---

## Cost Reference

| Operation | Cost (SOL) | Cost (USD) | Time |
|-----------|------------|-----------|------|
| Off-chain encode | FREE | FREE | 10-50ms |
| On-chain basic encode | 0.000005 | $0.00075 | 400ms |
| On-chain nanopore encode | 0.000008 | $0.0012 | 500ms |
| On-chain secure encode | 0.000010 | $0.0015 | 600ms |
| Safety screen (off-chain) | FREE | FREE | 50-100ms |
| Safety screen (on-chain) | 0.000006 | $0.0009 | 450ms |
| Verify transaction | FREE | FREE | 100ms |

---

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| API response (off-chain) | < 50ms | 95th percentile |
| API response (on-chain) | < 800ms | 95th percentile |
| Throughput | 1,000+ req/sec | Horizontal scaling |
| Uptime | 99.9% | Production |
| Concurrent users | 1,000+ | With load balancer |

---

## Safety Status Codes

| Status | Icon | Meaning | Action |
|--------|------|---------|--------|
| SAFE | ✅ | No risks detected | Can proceed |
| CAUTION | ⚠️ | Some concerns | Review carefully |
| UNSAFE | ❌ | Pathogen detected | Do not synthesize |

---

## Error Codes

| Code | Name | Description |
|------|------|-------------|
| INVALID_SEQUENCE | Invalid DNA sequence | Sequence contains invalid bases |
| MISSING_MARKERS | Missing markers | Required markers not found |
| DECODE_FAILED | Decoding failed | Unable to decode sequence |
| ENCRYPTION_ERROR | Encryption error | Cryptographic operation failed |
| PASSWORD_REQUIRED | Password required | Secure mode requires password |
| PASSWORD_WEAK | Weak password | Password doesn't meet requirements |
| CHECKSUM_MISMATCH | Checksum mismatch | Data integrity check failed |

---

## Common Patterns

### Encode with Blockchain Storage (Rust)
```rust
use biocypher_backend::dna::basic::DNACrypto;
use biocypher_backend::solana::client::SolanaClient;

async fn encode_with_blockchain(message: &str) -> Result<String> {
    // 1. Encode off-chain (fast)
    let dna = DNACrypto::encode_message(message)?;

    // 2. Store on Solana (verifiable)
    let client = SolanaClient::new("https://api.devnet.solana.com")?;
    let tx_sig = client.store_dna(message, EncodingMode::Basic).await?;

    Ok(dna)
}
```

### Safety Screening (TypeScript)
```typescript
import { BioCypherAPI } from './api/biocypher';

const api = new BioCypherAPI();

async function screenDna(dnaSequence: string, verifyOnChain: boolean) {
  const result = await api.safetyScreenOnChain(dnaSequence);

  console.log(`Status: ${result.safety_status}`);
  console.log(`Risks: ${result.pathogen_analysis.risk_level}`);
  console.log(`Verified: ${result.transaction_signature}`);
}
```

---

## Testing Commands

```bash
# Run all tests
cargo test

# Run specific module tests
cargo test --package backend --lib dna::basic

# Run with output
cargo test -- --nocapture

# Run integration tests
cargo test --test integration_tests

# Run Solana program tests
anchor test

# Run specific test
anchor test --test biocypher_encoder
```

---

## Deployment Checklist

### Rust Backend
- [ ] Build release binary
- [ ] Create Docker image
- [ ] Configure environment variables
- [ ] Set up load balancer
- [ ] Configure TLS
- [ ] Set up monitoring

### Solana Programs
- [ ] Deploy to mainnet
- [ ] Verify programs
- [ ] Set up monitoring
- [ ] Configure upgrade authority
- [ ] Document program IDs

### Frontend
- [ ] Build production bundle
- [ ] Deploy to CDN
- [ ] Configure domain
- [ ] Set up analytics
- [ ] Test functionality

---

## Important Notes

### Algorithm Compatibility
- Rust implementations MUST match Python exactly
- Use same encoding tables
- Same marker sequences (ATCGATCG, CGATATCG)
- Same error correction logic
- Verify output matches Python for same inputs

### Solana Constraints
- Account size: Max 10KB
- Compute units: 200,000 CUs default
- Transaction size: 1232 bytes max
- Optimize for low CUs and small accounts

### Security
- Never log passwords or encryption keys
- Use secure random for salts/IVs
- Validate all inputs
- Use constant-time comparisons for crypto
- Keep dependencies updated

---

## Troubleshooting

### Solana Transaction Failed
```bash
# Check transaction details
solana confirm <signature> -v

# Check account data
solana account <account_address>

# Check program logs
solana logs <signature>
```

### Rust Build Errors
```bash
# Clean and rebuild
cargo clean && cargo build

# Update dependencies
cargo update

# Check for specific error
cargo build 2>&1 | grep error
```

### Test Failures
```bash
# Run tests with backtrace
RUST_BACKTRACE=1 cargo test

# Run tests with output
cargo test -- --show-output

# Run specific test
cargo test test_encode_basic
```

---

## Resources

### Documentation
- Project README: `docs/PROJECT_README.md`
- Implementation Plan: `tasks/DETAILED_IMPLEMENTATION_PLAN.md`
- Task List: `tasks/todo.md`
- Protocol Spec: `biocypher/PROTOCOL_SPECIFICATION.md`

### External Links
- Rust Book: https://doc.rust-lang.org/book/
- Actix-web: https://actix.rs/
- Solana Docs: https://docs.solana.com/
- Anchor Book: https://book.anchor-lang.com/
- Solana Explorer: https://explorer.solana.com/

### Support
- Solana Discord: https://discord.gg/solana
- Anchor Discord: https://discord.gg/anchor
- Rust Users Forum: https://users.rust-lang.org/

---

## Quick Decision Tree

```
Need to encode message?
├─ Simple message?
│  └─→ Use Basic Mode (fast, simple)
├─ Nanopore sequencing?
│  └─→ Use Nanopore Mode (optimized)
└─ Sensitive data?
   └─→ Use Secure Mode (encrypted)

Need to store result?
├─ Temporary/local use?
│  └─→ Off-chain (FREE, fast)
└─ Permanent/verifiable?
   └─→ On-chain (SOL cost, immutable)

Need safety screening?
├─ Quick check?
│  └─→ Off-chain (FREE, fast)
└─ Regulatory/audit trail?
   └─→ On-chain (SOL cost, verified)
```

---

**Last Updated:** 2025-01-20
**Status:** Ready to build! 🚀
