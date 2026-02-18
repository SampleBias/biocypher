//! Arcium MXE Integration Module
//!
//! Bi0cyph3r uses Arcium for MPC-encrypted DNA encoding. Messages stay encrypted
//! throughout computation—no server ever sees plaintext.
//!
//! ## Architecture
//!
//! ```text
//!   Client                Backend/API           Arcium MXE (Solana)
//!     │                        │                        │
//!     │  1. Encrypt message    │                        │
//!     │  2. POST /api/encode   │                        │
//!     │ ──────────────────────>│   (optional: proxy     │
//!     │                        │    to MXE via RPC)     │
//!     │                        │ ──────────────────────>│ 3. Queue computation
//!     │                        │                        │ 4. MPC cluster computes
//!     │                        │<──────────────────────│ 5. Callback with result
//!     │<──────────────────────│   Encrypted DNA        │
//!     │  6. Decrypt result     │                        │
//! ```
//!
//! ## Integration Options
//!
//! 1. **Frontend-direct**: Client encrypts, calls MXE via Solana RPC, decrypts.
//!    Use `@arcium-hq/client` in your frontend.
//!
//! 2. **Backend proxy**: Backend runs Node.js subprocess or uses a sidecar
//!    that invokes the MXE. Backend returns encrypted result to client.
//!
//! 3. **Hybrid**: Standard encode/decode for non-sensitive data; MXE for
//!    confidential messages (e.g. `/api/encode-private`).
//!
//! ## MXE Project
//!
//! The Arcium MXE lives in `biocypher-mxe/`. Build and test:
//!
//! ```bash
//! cd biocypher-mxe
//! arcium build
//! arcium test
//! ```
//!
//! See [docs/ARCIUM_EDUCATIONAL_GUIDE.md](../../../docs/ARCIUM_EDUCATIONAL_GUIDE.md) for details.

use actix_web::{web, HttpResponse};
use serde::Serialize;

#[derive(Serialize)]
pub struct ArciumInfo {
    pub mxe_project: &'static str,
    pub instructions: Vec<&'static str>,
    pub message_limit_bytes: u32,
    pub dna_output_bases: u32,
    pub docs_url: &'static str,
}

/// Returns Arcium MXE integration info for clients.
pub async fn arcium_info() -> HttpResponse {
    HttpResponse::Ok().json(ArciumInfo {
        mxe_project: "biocypher-mxe",
        instructions: vec!["encode_basic", "decode_basic"],
        message_limit_bytes: 4,
        dna_output_bases: 16,
        docs_url: "/docs/ARCIUM_EDUCATIONAL_GUIDE.md",
    })
}
