//! Bi0cyph3r Storage - On-chain attestation for encode, decode, and safety operations.
//!
//! Records store hashes (SHA-256 of sequence) for cost efficiency.
//! Full sequences are not stored on-chain.

use anchor_lang::prelude::*;

declare_id!("FtXEkJEXm8bJbEc9DHPwuV8W7C9PLdszt8vnzsDgk9Rj");

#[program]
pub mod biocypher_storage {
    use super::*;

    /// Attest that a message was encoded to DNA.
    /// PDA: ["encode", owner, sequence_hash]
    pub fn record_encode(
        ctx: Context<RecordEncode>,
        mode: u8,
        sequence_hash: [u8; 32],
        timestamp: i64,
    ) -> Result<()> {
        let record = &mut ctx.accounts.encode_record;
        record.owner = ctx.accounts.payer.key();
        record.mode = mode;
        record.sequence_hash = sequence_hash;
        record.timestamp = timestamp;
        record.bump = ctx.bumps.encode_record;
        Ok(())
    }

    /// Attest that DNA was decoded to a message.
    /// PDA: ["decode", owner, sequence_hash]
    pub fn record_decode(
        ctx: Context<RecordDecode>,
        mode: u8,
        sequence_hash: [u8; 32],
        timestamp: i64,
    ) -> Result<()> {
        let record = &mut ctx.accounts.decode_record;
        record.owner = ctx.accounts.payer.key();
        record.mode = mode;
        record.sequence_hash = sequence_hash;
        record.timestamp = timestamp;
        record.bump = ctx.bumps.decode_record;
        Ok(())
    }

    /// Attest that a sequence was safety-screened.
    /// PDA: ["safety", owner, sequence_hash]
    /// status: 0=Safe, 1=Caution, 2=Unsafe
    pub fn record_safety(
        ctx: Context<RecordSafety>,
        sequence_hash: [u8; 32],
        status: u8,
        timestamp: i64,
    ) -> Result<()> {
        require!(status <= 2, ErrorCode::InvalidSafetyStatus);
        let record = &mut ctx.accounts.safety_record;
        record.owner = ctx.accounts.payer.key();
        record.sequence_hash = sequence_hash;
        record.status = status;
        record.timestamp = timestamp;
        record.bump = ctx.bumps.safety_record;
        Ok(())
    }
}

#[account]
pub struct EncodeRecord {
    pub owner: Pubkey,
    pub mode: u8,
    pub sequence_hash: [u8; 32],
    pub timestamp: i64,
    pub bump: u8,
}

impl EncodeRecord {
    pub const LEN: usize = 32 + 1 + 32 + 8 + 1; // owner + mode + sequence_hash + timestamp + bump
}

#[account]
pub struct DecodeRecord {
    pub owner: Pubkey,
    pub mode: u8,
    pub sequence_hash: [u8; 32],
    pub timestamp: i64,
    pub bump: u8,
}

impl DecodeRecord {
    pub const LEN: usize = 32 + 1 + 32 + 8 + 1; // owner + mode + sequence_hash + timestamp + bump
}

#[account]
pub struct SafetyRecord {
    pub owner: Pubkey,
    pub sequence_hash: [u8; 32],
    pub status: u8,
    pub timestamp: i64,
    pub bump: u8,
}

impl SafetyRecord {
    pub const LEN: usize = 32 + 32 + 1 + 8 + 1; // owner + sequence_hash + status + timestamp + bump
}

#[derive(Accounts)]
#[instruction(mode: u8, sequence_hash: [u8; 32])]
pub struct RecordEncode<'info> {
    #[account(
        init,
        payer = payer,
        space = 8 + EncodeRecord::LEN,
        seeds = [b"encode", payer.key().as_ref(), &sequence_hash],
        bump
    )]
    pub encode_record: Account<'info, EncodeRecord>,

    #[account(mut)]
    pub payer: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
#[instruction(mode: u8, sequence_hash: [u8; 32])]
pub struct RecordDecode<'info> {
    #[account(
        init,
        payer = payer,
        space = 8 + DecodeRecord::LEN,
        seeds = [b"decode", payer.key().as_ref(), &sequence_hash],
        bump
    )]
    pub decode_record: Account<'info, DecodeRecord>,

    #[account(mut)]
    pub payer: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
#[instruction(sequence_hash: [u8; 32])]
pub struct RecordSafety<'info> {
    #[account(
        init,
        payer = payer,
        space = 8 + SafetyRecord::LEN,
        seeds = [b"safety", payer.key().as_ref(), &sequence_hash],
        bump
    )]
    pub safety_record: Account<'info, SafetyRecord>,

    #[account(mut)]
    pub payer: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[error_code]
pub enum ErrorCode {
    #[msg("Invalid safety status: must be 0 (Safe), 1 (Caution), or 2 (Unsafe)")]
    InvalidSafetyStatus,
}
