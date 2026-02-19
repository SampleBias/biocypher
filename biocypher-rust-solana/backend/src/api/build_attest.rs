//! Build attestation transaction for user wallet signing.

use std::str::FromStr;

use actix_web::{web, HttpResponse};
use base64::{engine::general_purpose::STANDARD as BASE64, Engine};
use serde::Deserialize;
use validator::Validate;

use crate::dna::EncodingMode;
use crate::error::Result;
use crate::models::SafetyStatus;
use crate::solana::{build_attest_transaction, hash_sequence};

#[derive(Debug, Deserialize, Validate)]
pub struct BuildAttestRequest {
    #[validate(length(min = 1))]
    pub operation: String,

    #[validate(length(min = 1))]
    pub sequence: String,

    #[serde(default)]
    pub mode: Option<EncodingMode>,

    #[serde(default)]
    pub status: Option<SafetyStatus>,

    #[validate(length(min = 32, max = 44))]
    pub payer: String,
}

pub async fn build_attest_transaction_handler(
    req: web::Json<BuildAttestRequest>,
) -> Result<HttpResponse> {
    if let Err(errors) = req.validate() {
        return Ok(HttpResponse::BadRequest().json(serde_json::json!({
            "error": "Validation failed",
            "details": errors
        })));
    }

    let payer = match solana_sdk::pubkey::Pubkey::from_str(&req.payer) {
        Ok(p) => p,
        Err(_) => {
            return Ok(HttpResponse::BadRequest().json(serde_json::json!({
                "error": "Invalid payer pubkey"
            })))
        }
    };

    let seq_hash = hash_sequence(&req.sequence);

    let mode = match req.operation.as_str() {
        "encode" | "decode" => req.mode,
        "safety" => None,
        _ => {
            return Ok(HttpResponse::BadRequest().json(serde_json::json!({
                "error": "operation must be encode, decode, or safety"
            })));
        }
    };

    let status = match req.operation.as_str() {
        "safety" => req.status,
        _ => None,
    };

    let tx_bytes = match build_attest_transaction(
        payer,
        &req.operation,
        seq_hash,
        mode,
        status,
    )
    .await
    {
        Ok(b) => b,
        Err(e) => {
            return Ok(HttpResponse::InternalServerError().json(serde_json::json!({
                "error": e.to_string()
            })))
        }
    };

    Ok(HttpResponse::Ok().json(serde_json::json!({
        "transaction": BASE64.encode(&tx_bytes)
    })))
}
