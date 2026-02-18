# Arcium Educational Guide

**Understanding MPC-Based Encrypted Computing on Solana**

---

## Table of Contents

1. [What is Arcium?](#1-what-is-arcium)
2. [Why Encrypted Computation Matters](#2-why-encrypted-computation-matters)
3. [Core Concepts Explained](#3-core-concepts-explained)
4. [How MPC Keeps Data Private](#4-how-mpc-keeps-data-private)
5. [The Computation Lifecycle](#5-the-computation-lifecycle)
6. [Encryption Under the Hood](#6-encryption-under-the-hood)
7. [Developer Workflow](#7-developer-workflow)
8. [Arcis: Writing Private Logic](#8-arcis-writing-private-logic)
9. [Limitations & Trade-offs](#9-limitations--trade-offs)
10. [Further Resources](#10-further-resources)

---

## 1. What is Arcium?

**Arcium** is a decentralized network that lets you run computations on **encrypted data** without ever decrypting it. Think of it as an "encrypted supercomputer" on Solana: your sensitive inputs stay encrypted from the moment they leave your device until the result comes back—and even the computers doing the work never see the plaintext.

### The Problem It Solves

Normally, to compute on data you must either:

- **Decrypt it** (risky: servers, logs, and breaches can expose it), or
- **Trust a single party** (e.g., a hardware enclave) to keep it secret.

Arcium uses **Multi-Party Computation (MPC)** so that multiple independent nodes jointly compute on secret-shared data. No single node ever sees the full plaintext, and the computation is verifiable on-chain.

### Key Properties

| Property | Meaning |
|----------|---------|
| **End-to-end encrypted** | Data is encrypted by the client and stays encrypted until the client decrypts the result |
| **Trustless** | No single trusted party; security comes from distributed MPC |
| **On-chain orchestration** | Solana coordinates scheduling, verification, and payments |
| **Developer-friendly** | Rust + Anchor; add privacy by marking functions as confidential |

---

## 2. Why Encrypted Computation Matters

### Use Cases

- **Confidential DeFi**: Dark pools, private order books—trade without front-running or leaking intent
- **Confidential Gaming**: Hidden moves, sealed bids, private game state
- **Secure AI**: Train or run inference on sensitive data without exposing it
- **Compliance**: Process regulated data (health, finance) while preserving privacy

### The BioCypher Angle

For DNA cryptography systems like BioCypher, encrypted computation means:

- Messages can be encoded to DNA **without the server ever seeing the plaintext**
- Safety screening can run on **encrypted sequences**
- On-chain attestation can prove correctness **without revealing the underlying data**

---

## 3. Core Concepts Explained

### MXE (MPC eXecution Environment)

An **MXE** is your application. It consists of:

- A **Solana program** (smart contract) that queues computations and handles callbacks
- **Confidential instructions** (circuits) written in Arcis that define what runs in MPC
- Configuration (cluster, encryption, performance)

When you run `arcium init my-app`, you create an MXE project.

### Arcis

**Arcis** is a Rust-based framework for writing MPC circuits. It extends Anchor with:

- `#[encrypted]` modules for confidential logic
- `#[instruction]` for entry points that run in MPC
- `Enc<Owner, T>` for encrypted data types

You write normal-looking Rust; the Arcis compiler turns it into circuits that run in MPC.

### MPC Cluster (Arx Nodes)

A **cluster** is a group of **Arx nodes** that run your computations. Each node holds a *share* of the secret data—no single node can reconstruct it. They run the same circuit, exchange messages, and produce an encrypted result that only the intended recipient can decrypt.

### Arcium Program

The **Arcium program** is a Solana program that:

- Assigns computations to clusters
- Manages a mempool of pending work
- Verifies that clusters executed correctly
- Handles fees and incentives

You don't write this program; you interact with it via the Arcium SDK.

---

## 4. How MPC Keeps Data Private

### Secret Sharing

Instead of one party holding the secret, it's split into **shares**:

- Each node gets a share
- No subset below the threshold can reconstruct the secret
- The circuit operates on shares; intermediate values stay secret-shared

### Why "Both Branches Execute" in If/Else

In MPC, `if (secret_condition) { A } else { B }` can't work like normal code: which branch runs would leak the condition. So Arcium evaluates **both** branches and then selects the result based on the secret condition. The execution pattern is fixed; only the final output depends on the secret.

### Trust Model

- **Dishonest majority** (e.g., Cerberus): Security even if most nodes are malicious
- **Honest-but-curious** (e.g., Manticore): Nodes follow the protocol but may try to learn extra information

You choose the protocol when configuring your MXE's cluster.

---

## 5. The Computation Lifecycle

```
┌─────────┐     ┌──────────────┐     ┌────────────────┐     ┌───────────────┐
│ Client  │────▶│ MXE Program  │────▶│ Arcium Program │────▶│ MPC Cluster   │
│         │     │ (your app)   │     │ (orchestrator) │     │ (computes)    │
└─────────┘     └──────────────┘     └────────────────┘     └───────────────┘
      │                   │                    │                      │
      │ 1. Encrypt        │ 2. Queue           │ 3. Assign            │ 4. Compute
      │    inputs         │    computation     │    to cluster        │    in MPC
      │                   │                    │                      │
      │                   │                    │◀──── 5. Callback ─────│
      │                   │◀─── 6. Verify ────│     (encrypted)       │
      │◀── 7. Decrypt ────│     & invoke       │                      │
      │    result         │                    │                      │
```

### Step-by-Step

1. **Client**: Encrypts inputs with a shared secret (x25519 + Rescue cipher)
2. **Client → MXE**: Invokes your Solana instruction with encrypted params
3. **MXE → Arcium**: Queues the computation in the cluster's mempool
4. **Arcium → Cluster**: Cluster fetches work, runs MPC, produces encrypted result
5. **Cluster → Arcium**: Submits callback with signed, encrypted output
6. **Arcium**: Verifies the result and invokes your MXE callback
7. **Client**: Decrypts the result using the shared secret

All orchestration and verification happen on Solana.

---

## 6. Encryption Under the Hood

### Key Exchange

- **Algorithm**: x25519 (Elliptic Curve Diffie-Hellman)
- **Flow**: Client has a keypair; MXE/cluster has a public key; they derive a shared secret
- **Purpose**: Only the client and the MXE can decrypt inputs and outputs

### Symmetric Cipher

- **Cipher**: Rescue (arithmetic-oriented, ZK-friendly)
- **Mode**: CTR (Counter)
- **Key derivation**: Rescue-Prime hash of the shared secret
- **Nonce**: 16 random bytes from the client; used for encryption and incremented for outputs

### Data Ownership

- **`Enc<Shared, T>`**: Client and MXE share the secret; both can decrypt
- **`Enc<Mxe, T>`**: Only the MXE (cluster) can decrypt; useful when the client shouldn't see the result

---

## 7. Developer Workflow

### Installation

```bash
curl --proto '=https' --tlsv1.2 -sSfL https://install.arcium.com/ | bash
```

Prerequisites: Docker, Anchor 0.32.1, Solana CLI 2.3.0, Rust, Yarn.

### Project Structure

```
my-mxe/
├── programs/
│   └── my_mxe/
│       └── src/lib.rs          # Solana program + Arcium instructions
├── encrypted-ixs/
│   └── src/lib.rs              # Arcis circuits (MPC logic)
├── tests/
│   └── my-mxe.ts               # TypeScript tests
├── Arcium.toml                 # Arcium config
└── Anchor.toml
```

### Commands

| Command | Purpose |
|---------|---------|
| `arcium init <name>` | Create new MXE project |
| `arcium build` | Build circuits and Solana program |
| `arcium test` | Run tests (local or devnet) |
| `arcium deploy` | Deploy to devnet/mainnet |

---

## 8. Arcis: Writing Private Logic

### Basic Pattern

```rust
use arcis::*;

#[encrypted]
mod circuits {
    use arcis::*;

    pub struct InputValues {
        v1: u8,
        v2: u8,
    }

    #[instruction]
    pub fn add_together(input_ctxt: Enc<Shared, InputValues>) -> Enc<Shared, u16> {
        let input = input_ctxt.to_arcis();   // Decrypt in MPC
        let sum = input.v1 as u16 + input.v2 as u16;
        input_ctxt.owner.from_arcis(sum)     // Encrypt result for client
    }
}
```

### Important Constraints

- **No strings**: Use `[u8; N]` or `b"..."` for fixed-size data
- **Fixed loops**: `for` bounds must be compile-time known
- **No `match`, `while`, `return`**: Use `if/else` and `for` instead
- **Output size**: Callback payload is limited (~1232 bytes)
- **Both branches execute**: `if/else` always runs both sides

### Supported Operations

- Arithmetic: `+`, `-`, `*`, `/`, `%`
- Comparisons: `==`, `!=`, `<`, `>`, etc.
- `for` loops with fixed bounds
- Arrays, structs, iterators (except `.filter()`)
- `Pack<T>` for compact on-chain storage

---

## 9. Limitations & Trade-offs

| Limitation | Implication |
|------------|--------------|
| Output ≤ ~1232 bytes | Design for compact results or chunked computations |
| No variable-length loops | Use fixed max sizes (e.g., max message length) |
| Circuit size | Large circuits may need offchain storage (IPFS, S3) |
| Latency | MPC is slower than plain computation; plan for async flow |
| Cost | Compute and storage have on-chain costs |

### When to Use Arcium

- **Good fit**: Sensitive inputs/outputs, need for verifiable private computation, Solana-native apps
- **Poor fit**: High-throughput, low-latency, non-sensitive batch processing

---

## 10. Further Resources

| Resource | URL |
|----------|-----|
| Arcium Docs | https://docs.arcium.com |
| Documentation Index (LLMs) | https://docs.arcium.com/llms.txt |
| Hello World Tutorial | https://docs.arcium.com/developers/hello-world |
| Installation | https://docs.arcium.com/developers/installation |
| Arcis Operations Reference | https://docs.arcium.com/developers/arcis/operations |
| TypeScript SDK | https://ts.arcium.com/api |
| Examples Repo | https://github.com/arcium-hq/examples |
| Discord | https://discord.gg/arcium |

---

*This guide is intended for educational use with the BioCypher project. For the latest details, always refer to the official Arcium documentation.*
