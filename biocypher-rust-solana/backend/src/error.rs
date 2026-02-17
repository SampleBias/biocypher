//! Error types for BioCypher backend

use actix_web::http::StatusCode;
use actix_web::HttpResponse;
use thiserror::Error;

/// Result type alias for BioCypher operations
pub type Result<T> = std::result::Result<T, BioCypherError>;

/// Main error type for BioCypher backend
#[derive(Error, Debug)]
pub enum BioCypherError {
    // DNA crypto errors
    #[error("DNA crypto error: {0}")]
    DNACrypto(#[from] DNACryptoError),

    // Safety screener errors
    #[error("Safety screener error: {0}")]
    SafetyScreener(#[from] SafetyScreenerError),

    // API errors
    #[error("API error: {0}")]
    Api(#[from] ApiError),

    // Validation errors
    #[error("Validation error: {0}")]
    Validation(String),

    // Solana errors (for Phase 2)
    #[error("Solana error: {0}")]
    Solana(String),

    // IO errors
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    // Generic errors
    #[error("Internal error: {0}")]
    Internal(String),
}

/// DNA crypto specific errors
#[derive(Error, Debug, Clone)]
pub enum DNACryptoError {
    #[error("Invalid binary pair: {0}")]
    InvalidBinaryPair(String),

    #[error("Invalid binary string: {0}")]
    InvalidBinary(String),

    #[error("Invalid DNA sequence: {0}")]
    InvalidSequence(String),

    #[error("Missing required markers")]
    MissingMarkers,

    #[error("Decoding failed: {0}")]
    DecodingFailed(String),

    #[error("Encoding failed: {0}")]
    EncodingFailed(String),

    #[error("Encryption error: {0}")]
    EncryptionError(String),

    #[error("Decryption error: {0}")]
    DecryptionError(String),

    #[error("Password required for secure mode")]
    PasswordRequired,

    #[error("Password too weak: {0}")]
    PasswordWeak(String),
}

/// Safety screener specific errors
#[derive(Error, Debug, Clone)]
pub enum SafetyScreenerError {
    #[error("Empty sequence provided")]
    EmptySequence,

    #[error("No valid DNA bases found in sequence")]
    NoValidBases,

    #[error("Pathogen detection error: {0}")]
    PathogenDetectionError(String),

    #[error("Analysis error: {0}")]
    AnalysisError(String),
}

/// API specific errors
#[derive(Error, Debug)]
pub enum ApiError {
    #[error("Request error: {0}")]
    Request(String),

    #[error("Response error: {0}")]
    Response(String),

    #[error("Rate limit exceeded")]
    RateLimitExceeded,

    #[error("Unauthorized")]
    Unauthorized,

    #[error("Forbidden")]
    Forbidden,

    #[error("Not found: {0}")]
    NotFound(String),

    #[error("Conflict: {0}")]
    Conflict(String),
}

impl actix_web::error::ResponseError for BioCypherError {
    fn error_response(&self) -> HttpResponse {
        HttpResponse::build(self.status_code()).json(serde_json::json!({
            "error": self.to_string(),
            "error_type": self.error_type()
        }))
    }

    fn status_code(&self) -> StatusCode {
        match self {
            BioCypherError::DNACrypto(_) => StatusCode::BAD_REQUEST,
            BioCypherError::SafetyScreener(_) => StatusCode::BAD_REQUEST,
            BioCypherError::Api(ApiError::Request(_)) => StatusCode::BAD_REQUEST,
            BioCypherError::Api(ApiError::Response(_)) => StatusCode::BAD_REQUEST,
            BioCypherError::Api(ApiError::RateLimitExceeded) => StatusCode::TOO_MANY_REQUESTS,
            BioCypherError::Api(ApiError::Unauthorized) => StatusCode::UNAUTHORIZED,
            BioCypherError::Api(ApiError::Forbidden) => StatusCode::FORBIDDEN,
            BioCypherError::Api(ApiError::NotFound(_)) => StatusCode::NOT_FOUND,
            BioCypherError::Api(ApiError::Conflict(_)) => StatusCode::CONFLICT,
            BioCypherError::Validation(_) => StatusCode::BAD_REQUEST,
            BioCypherError::Solana(_) => StatusCode::INTERNAL_SERVER_ERROR,
            BioCypherError::Io(_) => StatusCode::INTERNAL_SERVER_ERROR,
            BioCypherError::Internal(_) => StatusCode::INTERNAL_SERVER_ERROR,
        }
    }
}

impl BioCypherError {
    /// Get error type string
    fn error_type(&self) -> &'static str {
        match self {
            BioCypherError::DNACrypto(_) => "dna_crypto",
            BioCypherError::SafetyScreener(_) => "safety_screener",
            BioCypherError::Api(_) => "api",
            BioCypherError::Validation(_) => "validation",
            BioCypherError::Solana(_) => "solana",
            BioCypherError::Io(_) => "io",
            BioCypherError::Internal(_) => "internal",
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_display() {
        let error = DNACryptoError::InvalidBinaryPair("00".to_string());
        assert_eq!(error.to_string(), "Invalid binary pair: 00");
    }

    #[test]
    fn test_safety_screener_error() {
        let error = SafetyScreenerError::EmptySequence;
        assert_eq!(error.to_string(), "Empty sequence provided");
    }

    #[test]
    fn test_error_conversion() {
        let dna_error: BioCypherError = DNACryptoError::PasswordRequired.into();
        assert!(matches!(dna_error, BioCypherError::DNACrypto(_)));
    }
}
