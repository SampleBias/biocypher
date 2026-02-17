//! Safety screening API endpoint

use actix_web::{web, HttpResponse};
use tracing::{info, error, instrument};
use validator::Validate;

use crate::safety::DNASafetyScreener;
use crate::error::Result;
use crate::models::{SafetyScreenRequest, SafetyScreenResponse};

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

    // TODO: Verify on blockchain if requested (Phase 2)
    let transaction_signature = if verify_on_chain {
        None // Will implement in Phase 2
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
