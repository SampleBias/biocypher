# BioCypher Rust + Solana Migration - Project Context

## Quick Start for AI Agents

**Project**: Convert BioCypher DNA cryptography system from Python/Flask to Rust backend with Solana blockchain integration

**Current State**: Planning complete, ready to begin Phase 1

**Architecture**: Hybrid - Rust backend handles fast operations, Solana handles verifiable storage

**Estimated Timeline**: 7 weeks

**Primary Language**: Rust (backend), Anchor (Solana programs), TypeScript (frontend)

---

## Project Overview

### What is BioCypher?

BioCypher is a DNA cryptography system that encodes digital messages into DNA sequences. It supports three encoding modes:

1. **Basic Mode**: Simple binary-to-DNA mapping (A=00, T=01, C=10, G=11)
2. **Nanopore Mode**: Optimized for nanopore sequencing with error correction, homopolymer avoidance, and GC balancing
3. **Secure Mode**: AES-256-CBC encryption + DNA encoding for secure data storage

Additional features:
- **Safety Screener**: Analyzes DNA sequences for pathogen risks and natural genome occurrences
- **Comprehensive Statistics**: GC content, homopolymer analysis, nanopore compatibility
- **Web UI**: Flask application with modern interface

### Current Implementation

**Technology Stack**:
- Backend: Python 3.11 + Flask
- Crypto: cryptography library (AES-256), hashlib
- Frontend: HTML/CSS/JavaScript (basic)
- Deployment: Gunicorn (recommended)

**Key Files**:
- `biocypher/app.py` - Flask application with API endpoints
- `biocypher/dna_crypto.py` - Basic DNA encoding/decoding
- `biocypher/nanopore_dna_crypto.py` - Nanopore-optimized encoding
- `biocypher/secure_nanopore_dna_crypto.py` - AES-256 encryption + DNA
- `biocypher/safety_screener.py` - Pathogen detection and risk assessment
- `biocypher/config.py` - Configuration management

### Migration Goals

1. **Performance**: Rust for fast DNA operations (10-100x faster than Python)
2. **Blockchain Integration**: Solana for verifiable, immutable storage
3. **Modern Architecture**: Microservices-ready, horizontally scalable
4. **Cost Efficiency**: Only pay for blockchain when verification is needed
5. **Developer Experience**: Type-safe, memory-safe code with excellent tooling

---

## Architecture Decisions

### Why Hybrid Architecture?

**Decision**: Rust backend (off-chain) + Solana blockchain (on-chain)

**Rationale**:
- ✅ **Performance**: Rust handles fast crypto operations without blockchain latency
- ✅ **Flexibility**: Users can choose fast off-chain or verifiable on-chain per operation
- ✅ **Cost Efficiency**: Only pay Solana transaction costs when blockchain benefits are needed
- ✅ **User Experience**: Quick response times for most operations
- ✅ **Scalability**: Horizontal scaling of Rust backend + Solana's high throughput
- ✅ **Fallback**: Can operate off-chain if Solana is congested

**Alternatives Considered**:
- ❌ **100% On-Chain**: Too expensive, slow, poor UX
- ❌ **100% Off-Chain**: No verification benefits, misses opportunity for blockchain trust
- ❌ **Different Blockchain**: Solana chosen for speed, low cost, Rust support

### Why Rust?

- Memory safety (no buffer overflows, null pointer issues)
- Performance (comparable to C/C++)
- Modern tooling (cargo, rustfmt, clippy)
- Excellent async support (tokio)
- Growing ecosystem
- WebAssembly support (future)
- **Solana programs are written in Rust/Anchor**

### Why Solana?

- High throughput (65,000+ TPS)
- Low transaction costs (~$0.00025 per transaction)
- Rust-native (Anchor framework)
- Growing ecosystem
- Developer-friendly
- Fast finality (~400ms)

---

## Technical Specifications

### DNA Encoding Algorithms

#### Basic Mode Encoding
```rust
1. Convert message to binary (8 bits per character)
2. Group binary in pairs (00, 01, 10, 11)
3. Map pairs to DNA bases: 00=A, 01=T, 10=C, 11=G
4. Return DNA sequence

Example: "Hi" → 01001000 01101001 → TAAA TATA TAAA TATA
```

#### Nanopore Mode Encoding
```rust
1. Convert message to binary (8 bits per character + parity bit)
2. Apply error correction (triple redundancy) if enabled
3. Pad to multiple of 3 for triplet encoding
4. Map triplets to DNA triplets:
   - 000=ATC, 001=ATG, 010=ACT, 011=ACG
   - 100=TAG, 101=TAC, 110=TCG, 111=TCA
5. Add nanopore markers: ATCGATCG (start), CGATATCG (stop)
6. Return DNA sequence

Example: "Hello" → ATCGATCGATCATGACT...CGATATCG (~350 bases)
```

#### Secure Mode Encoding
```rust
1. Generate random salt (16 bytes) and IV (16 bytes)
2. Derive key from password using PBKDF2 (100,000 iterations, SHA-256)
3. Encrypt message using AES-256-CBC
4. Serialize: salt + iv + encrypted_data
5. Encode to Base64
6. Encode Base64 string to DNA using Basic Mode
7. Add markers: ATCGATCG (start), CGATATCG (stop)
8. Return DNA sequence
```

### Safety Screener Algorithm

```rust
1. Clean DNA sequence (remove non-ATCG characters)
2. Check for pathogen signatures:
   - Viral polymerase motifs
   - Toxin gene patterns
   - Antibiotic resistance markers
   - Virulence factors
3. Check for natural genome occurrences:
   - Housekeeping genes
   - E. coli signatures
   - Human genome signatures
4. Analyze sequence characteristics:
   - GC content (optimal: 40-60%)
   - Homopolymer runs
   - Open reading frames (ORFs)
   - Repetitive elements
5. Determine safety status:
   - SAFE (green): No risks detected
   - CAUTION (orange): Some concerns found
   - UNSAFE (red): Pathogen signatures detected
6. Generate recommendations
```

### Solana Program Design

#### DNA Record Account
```rust
pub struct DNARecord {
    pub owner: Pubkey,              // User's public key
    pub mode: EncodingMode,         // Basic/Nanopore/Secure
    pub message: String,            // Original message (max 1000 chars)
    pub dna_sequence: String,       // Encoded DNA (max 10000 bases)
    pub use_error_correction: bool,  // For nanopore mode
    pub timestamp: i64,             // Unix timestamp
}
```

#### Safety Report Account
```rust
pub struct SafetyReport {
    pub dna_sequence: String,       // Screened sequence
    pub safety_status: SafetyStatus, // Safe/Caution/Unsafe
    pub pathogen_risk: bool,        // Pathogen detected
    pub natural_occurrence: bool,   // Natural genome match
    pub gc_content: u8,             // GC content percentage
    pub homopolymer_count: u32,     // Number of homopolymer runs
    pub timestamp: i64,
}
```

---

## Project Structure

```
biocypher-rust-solana/
├── Cargo.toml                 # Workspace root
├── programs/                  # Solana programs (Anchor)
│   ├── biocypher-encoder/
│   │   ├── Anchor.toml
│   │   ├── Cargo.toml
│   │   └── src/
│   │       ├── lib.rs        # Main program entry
│   │       ├── state.rs      # Account definitions
│   │       ├── instructions.rs # Instruction handlers
│   │       ├── processor.rs  # Core logic
│   │       └── error.rs      # Error types
│   ├── biocypher-decoder/
│   ├── biocypher-safety/
│   └── biocypher-storage/
│
├── backend/                   # Rust backend service
│   ├── Cargo.toml
│   ├── src/
│   │   ├── main.rs           # Application entry point
│   │   ├── dna/
│   │   │   ├── mod.rs        # Module exports
│   │   │   ├── basic.rs      # Basic encoding/decoding
│   │   │   ├── nanopore.rs   # Nanopore-optimized encoding
│   │   │   ├── secure.rs     # AES-256 encryption + DNA
│   │   │   └── traits.rs     # Shared traits
│   │   ├── safety/
│   │   │   ├── mod.rs        # Module exports
│   │   │   ├── screener.rs   # Safety screening logic
│   │   │   └── pathogen_db.rs # Pathogen signatures
│   │   ├── solana/
│   │   │   ├── mod.rs        # Module exports
│   │   │   ├── client.rs     # Solana RPC client wrapper
│   │   │   ├── encoder.rs    # Encoder program interaction
│   │   │   ├── decoder.rs    # Decoder program interaction
│   │   │   └── safety.rs     # Safety program interaction
│   │   ├── api/
│   │   │   ├── mod.rs        # Module exports
│   │   │   ├── routes.rs     # HTTP route definitions
│   │   │   ├── handlers.rs   # Request handlers
│   │   │   └── models.rs     # Request/response models
│   │   ├── config.rs         # Configuration management
│   │   └── error.rs          # Error types
│   ├── tests/
│   │   ├── dna_crypto_tests.rs
│   │   ├── api_tests.rs
│   │   └── integration_tests.rs
│   └── Dockerfile
│
├── frontend/                  # React/TypeScript UI
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   ├── components/
│   │   │   ├── EncodeForm.tsx
│   │   │   ├── DecodeForm.tsx
│   │   │   ├── SafetyScreen.tsx
│   │   │   └── TransactionViewer.tsx
│   │   ├── api/
│   │   │   └── biocypher.ts  # API client
│   │   ├── types/
│   │   │   └── index.ts      # TypeScript types
│   │   └── App.tsx
│   └── public/
│
├── migration/                 # Migration utilities
│   ├── data-export.py        # Export from Python
│   └── data-import.rs        # Import to Rust
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── SOLANA_PROGRAMS.md
│
├── tasks/
│   ├── todo.md              # Task tracking
│   ├── DETAILED_IMPLEMENTATION_PLAN.md
│   └── TODO_RUST_SOLANA.md
│
└── biocypher/               # Original Python code (reference)
    ├── app.py
    ├── dna_crypto.py
    ├── nanopore_dna_crypto.py
    ├── secure_nanopore_dna_crypto.py
    └── safety_screener.py
```

---

## Key Dependencies

### Rust Backend
```toml
[dependencies]
# Web Framework
actix-web = "4.4"
actix-cors = "0.6"
tokio = { version = "1.35", features = ["full"] }

# Solana
solana-client = "1.17"
solana-sdk = "1.17"
anchor-client = "0.29"

# Serialization
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

# Cryptography
aes-gcm = "0.10"              # AES-256-GCM
pbkdf2 = { version = "0.12", features = ["password-hash"] }
sha2 = "0.10"
rand = "0.8"

# Utilities
thiserror = "1.0"
anyhow = "1.0"
tracing = "0.1"
regex = "1.10"
```

### Solana Programs
```toml
[dependencies]
anchor-lang = "0.29"
anchor-spl = "0.29"
```

### Frontend
```json
{
  "dependencies": {
    "react": "^18.2",
    "typescript": "^5.0",
    "@solana/web3.js": "^1.87",
    "@solana/wallet-adapter-react": "^0.15",
    "axios": "^1.6"
  }
}
```

---

## Environment Setup

### Prerequisites

```bash
# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Solana CLI
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"

# Anchor Framework
cargo install --git https://github.com/coral-xyz/anchor avm --locked --force
avm install latest
avm use latest

# Node.js (for frontend)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Python (for reference/migration)
python3 -m venv venv
source venv/bin/activate
pip install -r biocypher/requirements.txt
```

### Development Environment

```bash
# Start local Solana validator
solana-test-validator

# Start Rust backend (from backend/ directory)
cargo run

# Start frontend (from frontend/ directory)
npm install
npm start
```

---

## API Endpoints

### Existing Python API (Reference)
```
POST /api/encode           - Encode message to DNA
POST /api/decode           - Decode DNA to message
POST /api/safety_screen    - Screen DNA for safety
```

### New Rust API

#### Encoding
```
POST /api/encode
Request:
{
  "message": "Hello World",
  "mode": "basic | nanopore | secure",
  "password": "optional for secure mode",
  "store_on_chain": false
}

Response:
{
  "dna_sequence": "ATCGATCG...",
  "transaction_signature": "...",  // If store_on_chain=true
  "stats": {
    "length": 350,
    "gc_content": 48.5,
    "homopolymers": []
  }
}
```

#### Decoding
```
POST /api/decode
Request:
{
  "sequence": "ATCGATCG...",
  "mode": "basic | nanopore | secure",
  "password": "optional for secure mode",
  "decode_on_chain": false
}

Response:
{
  "decoded_message": "Hello World",
  "transaction_signature": "...",  // If decode_on_chain=true
  "stats": {...}
}
```

#### Safety Screening
```
POST /api/safety-screen
Request:
{
  "dna_sequence": "ATCGATCG...",
  "verify_on_chain": false
}

Response:
{
  "safety_status": "SAFE | CAUTION | UNSAFE",
  "safety_icon": "✅ | ⚠️ | ❌",
  "pathogen_analysis": {
    "pathogen_risk": false,
    "matches": [],
    "risk_level": "low"
  },
  "natural_occurrence": {
    "natural_occurrence": false,
    "matches": [],
    "organisms": []
  },
  "sequence_characteristics": {
    "gc_content": 48.5,
    "homopolymer_runs": [],
    "orfs": []
  },
  "recommendations": ["✅ Sequence appears safe for synthesis"],
  "transaction_signature": "..."  // If verify_on_chain=true
}
```

#### Verification
```
GET /api/verify/:signature
Response:
{
  "transaction": {...},
  "dna_record": {...},
  "verified": true
}
```

#### History
```
GET /api/history/:public_key?page=1&limit=10
Response:
{
  "records": [
    {
      "type": "encode | decode | safety",
      "mode": "basic | nanopore | secure",
      "dna_sequence": "...",
      "transaction_signature": "...",
      "timestamp": 1704067200
    }
  ],
  "total": 150,
  "page": 1
}
```

---

## Testing Strategy

### Unit Tests
- All DNA crypto functions (42 test cases from Python)
- Solana program instructions
- API handlers
- Safety screener logic

### Integration Tests
- End-to-end encode/decode flows
- On-chain storage and retrieval
- Safety screening
- Cross-mode compatibility

### Performance Tests
- API response time targets:
  - Off-chain encode: < 50ms
  - Off-chain decode: < 50ms
  - Off-chain safety screen: < 100ms
  - On-chain operations: < 800ms

### Security Tests
- Input validation
- SQL injection prevention (not applicable, no SQL)
- XSS prevention
- CSRF protection
- Rate limiting
- Cryptographic correctness

---

## Deployment Strategy

### Development
- Local Solana validator
- Local Rust backend (cargo run)
- Local frontend (npm start)

### Staging
- Solana devnet
- Containerized Rust backend
- Staging frontend deployment

### Production
- Solana mainnet
- Load-balanced Rust backend (multiple instances)
- CDN-hosted frontend
- Redis cache layer
- Monitoring and alerting

---

## Success Criteria

### Performance
- ✅ API response time < 100ms (off-chain)
- ✅ API response time < 1s (on-chain)
- ✅ Support 1,000+ concurrent users
- ✅ 99.9% uptime

### Functionality
- ✅ All Python features ported to Rust
- ✅ Solana programs deployed and working
- ✅ On-chain storage and verification working
- ✅ Safety screening accurate (matches Python)

### Security
- ✅ No critical vulnerabilities
- ✅ Passed external security audit
- ✅ No data breaches in first 3 months

### Adoption
- ✅ 10,000+ encodes in first month
- ✅ 20%+ usage of on-chain features
- ✅ 95%+ user satisfaction

---

## Important Notes for AI Agents

### Code Porting Guidelines

1. **Exact Algorithm Matching**: Rust implementations must match Python algorithms exactly
   - Use same encoding tables
   - Same marker sequences (ATCGATCG, CGATATCG)
   - Same error correction logic
   - Same safety screening rules

2. **Error Handling**: Rust uses `Result<T, E>` instead of exceptions
   - Define custom error types using `thiserror`
   - Propagate errors with `?` operator
   - Provide helpful error messages

3. **String Handling**: Rust strings are UTF-8 by default
   - For DNA, treat as ASCII (only A, T, C, G)
   - Use `chars().nth()` for character access
   - Be careful with indexing

4. **Testing**: Port all Python test cases to Rust
   - Basic mode: 10 test cases
   - Nanopore mode: 17 test cases
   - Secure mode: 15 test cases
   - Safety screener: Multiple test vectors

5. **Solana Constraints**:
   - Account size limits: max 10KB per account
   - Compute unit limits: 200,000 CUs default
   - Transaction size: 1232 bytes max
   - Optimize for low CUs and small accounts

### Common Pitfalls

1. **Off-by-one errors**: Be careful with byte vs character indexing
2. **Binary string parsing**: Handle odd-length binary correctly
3. **Padding**: Ensure proper padding in nanopore mode
4. **Marker handling**: Don't double-count markers in stats
5. **Solana PDA derivation**: Use correct seeds and bump

### When to Ask for Help

- Unclear about algorithm behavior (check Python code)
- Solana program errors (check Anchor docs)
- API design questions (consult architecture docs)
- Performance issues (profile before optimizing)
- Security concerns (consult security team)

---

## Resources

### Documentation
- Original Protocol: `biocypher/PROTOCOL_SPECIFICATION.md`
- Detailed Plan: `tasks/DETAILED_IMPLEMENTATION_PLAN.md`
- Task List: `tasks/todo.md`
- Architecture: This document

### External Resources
- Rust Book: https://doc.rust-lang.org/book/
- Actix-web Docs: https://actix.rs/
- Solana Docs: https://docs.solana.com/
- Anchor Framework: https://www.anchor-lang.com/
- Anchor Book: https://book.anchor-lang.com/

### Code References
- Python implementation: `biocypher/` directory
- Test cases: `biocypher/test_*.py` files

---

## Current Status

**Last Updated**: 2025-01-20

**Phase**: Ready to begin Phase 1 (Rust Backend Foundation)

**Completed**:
- ✅ Architecture analysis
- ✅ Technology stack selection
- ✅ Detailed implementation plan
- ✅ Task breakdown
- ✅ Project context documentation

**Next Steps**:
- Initialize Rust workspace
- Implement basic DNA crypto in Rust
- Create Actix-web server
- Write unit tests

---

## Contact & Support

For questions or issues:
1. Check documentation in `docs/` directory
2. Review task list in `tasks/todo.md`
3. Consult original Python implementation
4. Reference detailed implementation plan

**Project Lead**: James Utley
**Architecture**: Hybrid (Rust + Solana)
**Timeline**: 7 weeks
**Confidence**: HIGH

---

**Remember**: This is a migration project. The goal is to maintain exact algorithm compatibility while improving performance and adding blockchain capabilities. Always verify Rust output matches Python output for the same inputs!
