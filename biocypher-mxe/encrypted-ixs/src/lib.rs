//! Bi0cyph3r MXE - Encrypted DNA Encoding Circuits
//!
//! Basic DNA encoding: 00→A(0), 01→T(1), 10→C(2), 11→G(3)
//! Each byte produces 4 DNA bases (2 bits per base).

use arcis::*;

/// Message length in bytes (4 bytes = 32 bits = 16 DNA bases)
const MSG_LEN: usize = 4;
/// DNA output length (4 bases per byte)
const DNA_LEN: usize = MSG_LEN * 4;

#[encrypted]
mod circuits {
    use arcis::*;

    use super::{DNA_LEN, MSG_LEN};

    /// Encode a message to DNA sequence using Basic mode.
    ///
    /// Mapping: 00→A(0), 01→T(1), 10→C(2), 11→G(3)
    /// Each byte produces 4 DNA bases from its 8 bits (2 bits per base).
    ///
    /// # Arguments
    /// * `input_ctxt` - Encrypted message bytes (4 bytes)
    ///
    /// # Returns
    /// * Encrypted DNA sequence as [u8; 16] where 0=A, 1=T, 2=C, 3=G
    #[instruction]
    pub fn encode_basic(input_ctxt: Enc<Shared, [u8; MSG_LEN]>) -> Enc<Shared, [u8; DNA_LEN]> {
        let message = input_ctxt.to_arcis();
        let mut dna = [0u8; DNA_LEN];

        for i in 0..MSG_LEN {
            let byte = message[i];
            // Extract 4 pairs of bits: (b>>6)&3, (b>>4)&3, (b>>2)&3, b&3
            let base0 = (byte >> 6) & 3u8;
            let base1 = (byte >> 4) & 3u8;
            let base2 = (byte >> 2) & 3u8;
            let base3 = byte & 3u8;
            dna[i * 4] = base0;
            dna[i * 4 + 1] = base1;
            dna[i * 4 + 2] = base2;
            dna[i * 4 + 3] = base3;
        }

        input_ctxt.owner.from_arcis(dna)
    }

    /// Decode a DNA sequence back to message bytes using Basic mode.
    ///
    /// Reverse mapping: A(0)→00, T(1)→01, C(2)→10, G(3)→11
    ///
    /// # Arguments
    /// * `input_ctxt` - Encrypted DNA sequence [u8; 16] (0=A, 1=T, 2=C, 3=G)
    ///
    /// # Returns
    /// * Encrypted message bytes [u8; 4]
    #[instruction]
    pub fn decode_basic(input_ctxt: Enc<Shared, [u8; DNA_LEN]>) -> Enc<Shared, [u8; MSG_LEN]> {
        let dna = input_ctxt.to_arcis();
        let mut message = [0u8; MSG_LEN];

        for i in 0..MSG_LEN {
            let b0 = dna[i * 4] & 3u8;
            let b1 = dna[i * 4 + 1] & 3u8;
            let b2 = dna[i * 4 + 2] & 3u8;
            let b3 = dna[i * 4 + 3] & 3u8;
            message[i] = (b0 << 6) | (b1 << 4) | (b2 << 2) | b3;
        }

        input_ctxt.owner.from_arcis(message)
    }
}
