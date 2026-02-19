//! Decode API endpoint

use actix_web::{web, HttpResponse};
use tracing::{info, error, instrument};
use validator::Validate;

use crate::dna::{
    basic::DNACrypto,
    nanopore::NanoporeDNACrypto,
    secure::SecureDNACrypto,
    split_key::SplitKeyDNACrypto,
    traits::{DNACoder, SequenceStats as TraitsSequenceStats},
};
use crate::error::Result;
use crate::models::{DecodeRequest, DecodeResponse, SequenceStats};
use crate::solana::{hash_sequence, SolanaClient};

/// Decode DNA sequence to message
#[instrument(skip(req))]
pub async fn decode_message(
    req: web::Json<DecodeRequest>,
) -> Result<HttpResponse> {
    // Validate request
    if let Err(errors) = req.validate() {
        error!("Validation errors: {:?}", errors);
        return Ok(HttpResponse::BadRequest().json(serde_json::json!({
            "error": "Validation failed",
            "details": errors
        })));
    }

    let DecodeRequest {
        sequence,
        mode,
        password,
        k1_base64,
        k2_base64,
        decode_on_chain,
    } = req.into_inner();

    info!("Decoding sequence (mode: {}, length: {})", mode, sequence.len());

    // Check password for secure mode
    if matches!(mode, crate::dna::EncodingMode::Secure) && password.is_none() {
        error!("Password required for secure mode");
        return Ok(HttpResponse::BadRequest().json(serde_json::json!({
            "error": "Password is required for secure mode"
        })));
    }

    // Check K1/K2 for split-key mode
    if matches!(mode, crate::dna::EncodingMode::SplitKey) {
        if k1_base64.is_none() || k2_base64.is_none() {
            error!("K1 and K2 required for split-key mode");
            return Ok(HttpResponse::BadRequest().json(serde_json::json!({
                "error": "K1 and K2 are required for split-key mode"
            })));
        }
    }

    // Decode based on mode
    let decoded_message = match mode {
        crate::dna::EncodingMode::Basic => DNACrypto::decode_sequence(&sequence)?,
        crate::dna::EncodingMode::Nanopore => NanoporeDNACrypto::decode_sequence(&sequence)?,
        crate::dna::EncodingMode::Secure => {
            let pwd = password.as_ref().expect("password validated above");
            SecureDNACrypto::decode_with_password(&sequence, pwd)?
        }
        crate::dna::EncodingMode::SplitKey => {
            let k1 = k1_base64.as_ref().expect("k1 validated above");
            let k2 = k2_base64.as_ref().expect("k2 validated above");
            SplitKeyDNACrypto::decode_with_split_keys(&sequence, k1, k2)?
        }
    };

    // Get statistics
    let stats = match mode {
        crate::dna::EncodingMode::Basic => DNACrypto::get_sequence_stats(&sequence),
        crate::dna::EncodingMode::Nanopore => NanoporeDNACrypto::get_sequence_stats(&sequence),
        crate::dna::EncodingMode::Secure => SecureDNACrypto::get_sequence_stats(&sequence),
        crate::dna::EncodingMode::SplitKey => SplitKeyDNACrypto::get_sequence_stats(&sequence),
    };

    let transaction_signature = if decode_on_chain {
        match SolanaClient::from_env() {
            Some(client) => {
                let seq_hash = hash_sequence(&sequence);
                match client.record_decode(mode, seq_hash).await {
                    Ok(sig) => Some(sig),
                    Err(e) => {
                        error!("Solana record_decode failed: {}", e);
                        return Ok(HttpResponse::InternalServerError().json(serde_json::json!({
                            "error": format!("Solana attestation failed: {}", e)
                        })));
                    }
                }
            }
            None => {
                error!("Solana not configured but decode_on_chain requested");
                return Ok(HttpResponse::BadRequest().json(serde_json::json!({
                    "error": "Solana attestation requested but not configured. Set SOLANA_KEYPAIR_PATH or connect a wallet."
                })));
            }
        }
    } else {
        None
    };

    let response = DecodeResponse {
        decoded_message,
        transaction_signature,
        stats: SequenceStats {
            length: stats.length,
            bases: crate::models::BaseCounts {
                a: stats.bases.a,
                t: stats.bases.t,
                c: stats.bases.c,
                g: stats.bases.g,
            },
            gc_content: stats.gc_content,
        },
    };

    info!("Decoding successful (length: {} chars)", response.decoded_message.len());

    Ok(HttpResponse::Ok().json(response))
}
