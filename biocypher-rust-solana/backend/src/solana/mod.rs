//! Solana integration for on-chain attestation.
//!
//! Records encode, decode, and safety attestations on the biocypher-storage program.
//! When SOLANA_RPC_URL or SOLANA_KEYPAIR_PATH are unset, all operations are no-op.

pub mod client;

pub use client::{hash_sequence, SolanaClient};
