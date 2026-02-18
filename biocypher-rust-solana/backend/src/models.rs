//! Request and response models for API

use serde::{Deserialize, Serialize};
use validator::Validate;

use crate::dna::EncodingMode;

/// Encode request model
#[derive(Debug, Clone, Deserialize, Validate)]
pub struct EncodeRequest {
    /// Message to encode
    #[validate(length(min = 1, max = 1000, message = "Message must be 1-1000 characters"))]
    pub message: String,

    /// Encoding mode
    #[serde(default = "default_encoding_mode")]
    pub mode: EncodingMode,

    /// Password for secure mode (required if mode == Secure)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub password: Option<String>,

    /// Store on blockchain (Phase 2)
    #[serde(default, skip_serializing_if = "is_false")]
    pub store_on_chain: bool,
}

/// Default encoding mode
fn default_encoding_mode() -> EncodingMode {
    EncodingMode::Basic
}

/// Check if value is false (for serde skip_serializing_if)
#[allow(dead_code)]
fn is_false(value: &bool) -> bool {
    !value
}

/// Encode response model
#[derive(Debug, Clone, Serialize)]
pub struct EncodeResponse {
    /// Encoded DNA sequence
    pub dna_sequence: String,

    /// Transaction signature (Phase 2)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub transaction_signature: Option<String>,

    /// Sequence statistics
    pub stats: SequenceStats,
}

/// Decode request model
#[derive(Debug, Clone, Deserialize, Validate)]
pub struct DecodeRequest {
    /// DNA sequence to decode
    #[validate(length(min = 1, max = 10000, message = "Sequence must be 1-10000 bases"))]
    pub sequence: String,

    /// Encoding mode
    #[serde(default = "default_encoding_mode")]
    pub mode: EncodingMode,

    /// Password for secure mode (required if mode == Secure)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub password: Option<String>,

    /// Decode on blockchain (Phase 2)
    #[serde(default, skip_serializing_if = "is_false")]
    pub decode_on_chain: bool,
}

/// Decode response model
#[derive(Debug, Clone, Serialize)]
pub struct DecodeResponse {
    /// Decoded message
    pub decoded_message: String,

    /// Transaction signature (Phase 2)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub transaction_signature: Option<String>,

    /// Sequence statistics
    pub stats: SequenceStats,
}

/// Safety screen request model
#[derive(Debug, Clone, Deserialize, Validate)]
pub struct SafetyScreenRequest {
    /// DNA sequence to screen
    #[validate(length(min = 1, max = 10000, message = "Sequence must be 1-10000 bases"))]
    pub dna_sequence: String,

    /// Verify on blockchain (Phase 2)
    #[serde(default, skip_serializing_if = "is_false")]
    pub verify_on_chain: bool,
}

/// Safety screen response model
#[derive(Debug, Clone, Serialize)]
pub struct SafetyScreenResponse {
    /// DNA sequence
    pub dna_sequence: String,

    /// Safety status
    pub safety_status: SafetyStatus,

    /// Safety icon
    pub safety_icon: &'static str,

    /// Pathogen analysis
    pub pathogen_analysis: PathogenAnalysis,

    /// Natural occurrence check
    pub natural_occurrence: NaturalOccurrence,

    /// Sequence characteristics
    pub sequence_characteristics: SequenceCharacteristics,

    /// Recommendations
    pub recommendations: Vec<String>,

    /// Transaction signature (Phase 2)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub transaction_signature: Option<String>,
}

/// Safety status enumeration
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "UPPERCASE")]
pub enum SafetyStatus {
    Safe,
    Caution,
    Unsafe,
}

/// Safety status icon mapping
impl SafetyStatus {
    pub fn icon(&self) -> &'static str {
        match self {
            SafetyStatus::Safe => "✅",
            SafetyStatus::Caution => "⚠️",
            SafetyStatus::Unsafe => "❌",
        }
    }

    pub fn color(&self) -> &'static str {
        match self {
            SafetyStatus::Safe => "green",
            SafetyStatus::Caution => "orange",
            SafetyStatus::Unsafe => "red",
        }
    }
}

/// Pathogen analysis result
#[derive(Debug, Clone, Serialize)]
pub struct PathogenAnalysis {
    /// Pathogen risk detected
    pub pathogen_risk: bool,

    /// Matching signatures
    pub matches: Vec<PathogenMatch>,

    /// Risk level
    pub risk_level: RiskLevel,
}

/// Pathogen signature match
#[derive(Debug, Clone, Serialize)]
pub struct PathogenMatch {
    /// Category of pathogen
    pub category: String,

    /// Matching signature
    pub signature: String,

    /// Position in sequence
    pub position: usize,
}

/// Risk level enumeration
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum RiskLevel {
    Low,
    Medium,
    High,
}

/// Natural occurrence result
#[derive(Debug, Clone, Serialize)]
pub struct NaturalOccurrence {
    /// Natural occurrence detected
    pub natural_occurrence: bool,

    /// Matching signatures
    pub matches: Vec<NaturalMatch>,

    /// Organisms found
    pub organisms: Vec<String>,
}

/// Natural genome match
#[derive(Debug, Clone, Serialize)]
pub struct NaturalMatch {
    /// Type of match
    #[serde(rename = "type")]
    pub match_type: String,

    /// Gene or organism name
    pub name: String,

    /// Matching signature
    pub signature: String,

    /// Position in sequence
    pub position: usize,
}

/// Sequence characteristics
#[derive(Debug, Clone, Serialize)]
pub struct SequenceCharacteristics {
    /// Sequence length
    pub length: usize,

    /// GC content percentage
    pub gc_content: f64,

    /// Homopolymer runs
    pub homopolymer_runs: Vec<HomopolymerRun>,

    /// Open reading frames
    pub orfs: Vec<OpenReadingFrame>,

    /// Repetitive elements
    pub repetitive_elements: Vec<RepetitiveElement>,

    /// Warnings
    pub warnings: Vec<String>,
}

/// Homopolymer run
#[derive(Debug, Clone, Serialize)]
pub struct HomopolymerRun {
    /// Base character
    pub base: char,

    /// Run length
    pub length: usize,

    /// Start position
    pub position: usize,
}

/// Open reading frame
#[derive(Debug, Clone, Serialize)]
pub struct OpenReadingFrame {
    /// Start position
    pub start: usize,

    /// End position
    pub end: usize,

    /// Reading frame
    pub frame: usize,
}

/// Repetitive element
#[derive(Debug, Clone, Serialize)]
pub struct RepetitiveElement {
    /// Pattern
    pub pattern: String,

    /// Count
    pub count: usize,

    /// Pattern length
    pub length: usize,
}

/// Sequence statistics (simplified version)
#[derive(Debug, Clone, Serialize)]
pub struct SequenceStats {
    /// Sequence length
    pub length: usize,

    /// Base counts
    pub bases: BaseCounts,

    /// GC content percentage
    pub gc_content: f64,
}

/// Base count statistics
#[derive(Debug, Clone, Serialize)]
pub struct BaseCounts {
    pub a: usize,
    pub t: usize,
    pub c: usize,
    pub g: usize,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_safety_status_icon() {
        assert_eq!(SafetyStatus::Safe.icon(), "✅");
        assert_eq!(SafetyStatus::Caution.icon(), "⚠️");
        assert_eq!(SafetyStatus::Unsafe.icon(), "❌");
    }

    #[test]
    fn test_safety_status_color() {
        assert_eq!(SafetyStatus::Safe.color(), "green");
        assert_eq!(SafetyStatus::Caution.color(), "orange");
        assert_eq!(SafetyStatus::Unsafe.color(), "red");
    }

    #[test]
    fn test_default_encoding_mode() {
        assert_eq!(default_encoding_mode(), EncodingMode::Basic);
    }

    #[test]
    fn test_is_false() {
        assert!(is_false(&false));
        assert!(!is_false(&true));
    }
}
