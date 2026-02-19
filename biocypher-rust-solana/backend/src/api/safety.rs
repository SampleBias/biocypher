//! Safety screening API endpoint

use actix_web::{web, HttpResponse};
use tracing::{info, error, instrument};
use validator::Validate;

use crate::error::Result;
use crate::models::{SafetyScreenRequest, SafetyScreenResponse};
use crate::safety::DNASafetyScreener;
use crate::solana::{hash_sequence, SolanaClient};

/// Screen DNA sequence for safety
#[instrument(skip(req))]
pub async fn safety_screen(
    req: web::Json<SafetyScreenRequest>,
) -> Result<HttpResponse> {
    // Validate request
    if let Err(errors) = req.validate() {
        error!("Validation errors: {:?}", errors);
        return Ok(HttpResponse::BadRequest().json(serde_json::json!({
            "error": "Validation failed",
            "details": errors
        })));
    }

    let SafetyScreenRequest {
        dna_sequence,
        verify_on_chain,
    } = req.into_inner();

    info!("Screening DNA sequence (length: {})", dna_sequence.len());

    // Perform safety screening
    let screener = DNASafetyScreener::new();
    let report = screener.perform_comprehensive_screening(&dna_sequence)?;

    let transaction_signature = if verify_on_chain {
        match SolanaClient::from_env() {
            Some(client) => {
                let seq_hash = hash_sequence(&dna_sequence);
                match client.record_safety(seq_hash, report.safety_status).await {
                    Ok(sig) => Some(sig),
                    Err(e) => {
                        error!("Solana record_safety failed: {}", e);
                        None
                    }
                }
            }
            None => None,
        }
    } else {
        None
    };

    let response = SafetyScreenResponse {
        dna_sequence: report.dna_sequence,
        safety_status: report.safety_status,
        safety_icon: report.safety_status.icon(),
        pathogen_analysis: report.pathogen_analysis,
        natural_occurrence: report.natural_occurrence,
        sequence_characteristics: report.sequence_characteristics,
        recommendations: report.recommendations,
        transaction_signature,
    };

    info!("Safety screening complete (status: {:?})", response.safety_status);

    Ok(HttpResponse::Ok().json(response))
}
