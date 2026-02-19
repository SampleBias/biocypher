//! Encode API endpoint

use actix_web::{web, HttpResponse};
use tracing::{info, error, instrument};
use validator::Validate;

use crate::dna::{
    basic::DNACrypto,
    nanopore::NanoporeDNACrypto,
    secure::SecureDNACrypto,
    traits::{DNACoder, SequenceStats as TraitsSequenceStats},
};
use crate::error::Result;
use crate::models::{EncodeRequest, EncodeResponse, SequenceStats};
use crate::solana::{hash_sequence, SolanaClient};

/// Encode message to DNA
#[instrument(skip(req))]
pub async fn encode_message(
    req: web::Json<EncodeRequest>,
) -> Result<HttpResponse> {
    // Validate request
    if let Err(errors) = req.validate() {
        error!("Validation errors: {:?}", errors);
        return Ok(HttpResponse::BadRequest().json(serde_json::json!({
            "error": "Validation failed",
            "details": errors
        })));
    }

    let EncodeRequest {
        message,
        mode,
        password,
        store_on_chain,
    } = req.into_inner();

    info!("Encoding message (mode: {}, length: {})", mode, message.len());

    // Check password for secure mode
    if matches!(mode, crate::dna::EncodingMode::Secure) && password.is_none() {
        error!("Password required for secure mode");
        return Ok(HttpResponse::BadRequest().json(serde_json::json!({
            "error": "Password is required for secure mode"
        })));
    }

    // Encode based on mode
    let dna_sequence = match mode {
        crate::dna::EncodingMode::Basic => DNACrypto::encode_message(&message)?,
        crate::dna::EncodingMode::Nanopore => NanoporeDNACrypto::encode_message(&message)?,
        crate::dna::EncodingMode::Secure => {
            let pwd = password.as_ref().expect("password validated above");
            SecureDNACrypto::encode_with_password(&message, pwd)?
        }
    };

    // Get statistics (use appropriate stats for each mode)
    let stats = match mode {
        crate::dna::EncodingMode::Basic => DNACrypto::get_sequence_stats(&dna_sequence),
        crate::dna::EncodingMode::Nanopore => NanoporeDNACrypto::get_sequence_stats(&dna_sequence),
        crate::dna::EncodingMode::Secure => SecureDNACrypto::get_sequence_stats(&dna_sequence),
    };

    let transaction_signature = if store_on_chain {
        match SolanaClient::from_env() {
            Some(client) => {
                let seq_hash = hash_sequence(&dna_sequence);
                match client.record_encode(mode, seq_hash).await {
                    Ok(sig) => Some(sig),
                    Err(e) => {
                        error!("Solana record_encode failed: {}", e);
                        None
                    }
                }
            }
            None => None,
        }
    } else {
        None
    };

    let response = EncodeResponse {
        dna_sequence,
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

    info!("Encoding successful (length: {} bases)", response.dna_sequence.len());

    Ok(HttpResponse::Ok().json(response))
}
