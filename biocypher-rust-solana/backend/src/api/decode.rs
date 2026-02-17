//! Decode API endpoint

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
use crate::models::{
    DecodeRequest, DecodeResponse, SequenceStats,
};

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

    // Decode based on mode
    let decoded_message = match mode {
        crate::dna::EncodingMode::Basic => DNACrypto::decode_sequence(&sequence)?,
        crate::dna::EncodingMode::Nanopore => NanoporeDNACrypto::decode_sequence(&sequence)?,
        crate::dna::EncodingMode::Secure => {
            let pwd = password.as_ref().expect("password validated above");
            SecureDNACrypto::decode_with_password(&sequence, pwd)?
        }
    };

    // Get statistics
    let stats = match mode {
        crate::dna::EncodingMode::Basic => DNACrypto::get_sequence_stats(&sequence),
        crate::dna::EncodingMode::Nanopore => NanoporeDNACrypto::get_sequence_stats(&sequence),
        crate::dna::EncodingMode::Secure => SecureDNACrypto::get_sequence_stats(&sequence),
    };

    // TODO: Decode on blockchain if requested (Phase 2)
    let transaction_signature = if decode_on_chain {
        None // Will implement in Phase 2
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
