# Bi0cyph3r Arcium Service

Node.js HTTP service for Arcium MPC encode/decode. Uses Solana CLI keypair (`~/.config/solana/id.json`).

## Prerequisites

- Node.js 18+
- Solana CLI configured (`solana config set --keypair ~/.config/solana/id.json`)
- Arcium CLI, Anchor, biocypher-mxe built (`cd biocypher-mxe && arcium build`)
- Arcium localnet or devnet running

## Quick Start

```bash
# From repo root
./run-arcium-service.sh
```

Or manually:

```bash
cd biocypher-mxe
MXE_PATH=. node ../biocypher-arcium-service/dist/index.js
```

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| ARCIUM_SERVICE_PORT | 3001 | HTTP port |
| RPC_URL | http://127.0.0.1:8899 | Solana RPC (localnet) |
| KEYPAIR_PATH | ~/.config/solana/id.json | Solana keypair |
| MXE_PATH | process.cwd() | Path to biocypher-mxe |
| MXE_PROGRAM_ID | BioCyphMXE11111111111111111111111111111111 | Program ID |
| MANUFACTURER_API_URL | (empty) | DNA manufacturer API endpoint (Twist, IDT, etc.) |
| TRANSMIT_MOCK | false | If true, accept transmissions without forwarding |
| USE_BUILTIN_MOCK | false | If true, forward to built-in /transmit-receive for testing |

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Service health |
| GET | /status | Arcium readiness (connects to MXE) |
| POST | /encode-mpc | Encode 4 bytes → 16 DNA bases |
| POST | /decode-mpc | Decode 16 DNA bases → 4 bytes |
| POST | /transmit-secure | Forward encrypted plasmid to manufacturer API |
| POST | /transmit-receive | Mock manufacturer receiver (for testing) |

## Mock Manufacturer Testing

To test the secure transmission flow end-to-end without a real manufacturer API:

```bash
USE_BUILTIN_MOCK=true node dist/index.js
```

Then design a plasmid in the Web UI, connect Arcium, and click **Transmit to Manufacturer**. The encrypted payload will be forwarded to the built-in `/transmit-receive` endpoint, which logs the transmission and returns success.

## Limits

- **Encode**: Max 4 bytes (characters)
- **Decode**: Exactly 16 DNA bases (ATCG)

## Build

```bash
npm install
npm run build
```
