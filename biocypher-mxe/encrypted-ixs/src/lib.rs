//! Bi0cyph3r MXE - Encrypted DNA Encoding Circuits
//!
//! Basic DNA encoding: 00→A(0), 01→T(1), 10→C(2), 11→G(3)
//! Each byte produces 4 DNA bases (2 bits per base).
//!
//! Arcis constraints: no `use super`, no `<<` (use * instead).

use arcis::*;

#[encrypted]
mod circuits {
    use arcis::*;

    /// Encode a message to DNA sequence using Basic mode.
    /// Mapping: 00→A(0), 01→T(1), 10→C(2), 11→G(3)
    #[instruction]
    pub fn encode_basic(input_ctxt: Enc<Shared, [u8; 4]>) -> Enc<Shared, [u8; 16]> {
        let message = input_ctxt.to_arcis();
        let mut dna = [0u8; 16];

        for i in 0..4 {
            let byte = message[i];
            // Extract 4 pairs of bits using / and % (no >> or & on encrypted ints)
            let base0 = (byte / 64) % 4;
            let base1 = (byte / 16) % 4;
            let base2 = (byte / 4) % 4;
            let base3 = byte % 4;
            dna[i * 4] = base0;
            dna[i * 4 + 1] = base1;
            dna[i * 4 + 2] = base2;
            dna[i * 4 + 3] = base3;
        }

        input_ctxt.owner.from_arcis(dna)
    }

    /// Decode a DNA sequence back to message bytes using Basic mode.
    /// Reverse mapping: A(0)→00, T(1)→01, C(2)→10, G(3)→11
    /// Note: << is unsupported in Arcis; use multiplication instead.
    #[instruction]
    pub fn decode_basic(input_ctxt: Enc<Shared, [u8; 16]>) -> Enc<Shared, [u8; 4]> {
        let dna = input_ctxt.to_arcis();
        let mut message = [0u8; 4];

        for i in 0..4 {
            let b0 = dna[i * 4] % 4;
            let b1 = dna[i * 4 + 1] % 4;
            let b2 = dna[i * 4 + 2] % 4;
            let b3 = dna[i * 4 + 3] % 4;
            // b0<<6 | b1<<4 | b2<<2 | b3 = b0*64 + b1*16 + b2*4 + b3
            message[i] = (b0 * 64) + (b1 * 16) + (b2 * 4) + b3;
        }

        input_ctxt.owner.from_arcis(message)
    }
}
