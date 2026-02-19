//! Solana integration API — status and attestation info.

use actix_web::HttpResponse;
use serde::Serialize;

use crate::solana::SolanaClient;

#[derive(Serialize)]
pub struct SolanaInfo {
    pub configured: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub wallet_pubkey: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub program_id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rpc_url: Option<String>,
}

/// Returns Solana attestation status for clients.
pub async fn solana_info() -> HttpResponse {
    match SolanaClient::from_env() {
        Some(client) => {
            let wallet_pubkey = client.wallet_pubkey().map(|p| p.to_string());
            let program_id = Some(client.program_id().to_string());
            let rpc_url = Some(client.rpc_url().to_string());
            HttpResponse::Ok().json(SolanaInfo {
                configured: true,
                wallet_pubkey,
                program_id,
                rpc_url,
            })
        }
        None => {
            let rpc_url = std::env::var("SOLANA_RPC_URL")
                .unwrap_or_else(|_| "https://api.devnet.solana.com".to_string());
            HttpResponse::Ok().json(SolanaInfo {
                configured: false,
                wallet_pubkey: None,
                program_id: None,
                rpc_url: Some(rpc_url),
            })
        }
    }
}
