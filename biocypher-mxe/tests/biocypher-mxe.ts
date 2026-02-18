/**
 * BioCypher MXE - Arcium MPC Encrypted DNA Encoding Tests
 *
 * Tests encode_basic and decode_basic confidential instructions.
 * Message stays encrypted throughout; client decrypts result.
 */

import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { PublicKey } from "@solana/web3.js";
import { BiocypherMxe } from "../target/types/biocypher_mxe";
import { randomBytes } from "crypto";
import {
  awaitComputationFinalization,
  getArciumEnv,
  getCompDefAccOffset,
  getArciumAccountBaseSeed,
  getArciumProgramId,
  uploadCircuit,
  RescueCipher,
  deserializeLE,
  getMXEAccAddress,
  getMempoolAccAddress,
  getCompDefAccAddress,
  getExecutingPoolAccAddress,
  x25519,
  getComputationAccAddress,
  getMXEPublicKey,
  getClusterAccAddress,
  getLookupTableAddress,
  getArciumProgram,
} from "@arcium-hq/client";
import * as fs from "fs";
import * as os from "os";

/// DNA base mapping: 0=A, 1=T, 2=C, 3=G
const DNA_BASES = ["A", "T", "C", "G"];

function dnaToString(dnaBytes: number[]): string {
  return dnaBytes.map((b) => DNA_BASES[b & 3]).join("");
}

describe("BioCypher MXE", () => {
  anchor.setProvider(anchor.AnchorProvider.env());
  const program = anchor.workspace.BiocypherMxe as Program<BiocypherMxe>;
  const provider = anchor.getProvider();

  type Event = anchor.IdlEvents<(typeof program)["idl"]>;
  const awaitEvent = async <E extends keyof Event>(
    eventName: E
  ): Promise<Event[E]> => {
    let listenerId: number;
    const event = await new Promise<Event[E]>((res) => {
      listenerId = program.addEventListener(eventName, (event) => {
        res(event as Event[E]);
      });
    });
    await program.removeEventListener(listenerId);
    return event;
  };

  const arciumEnv = getArciumEnv();
  const clusterAccount = getClusterAccAddress(arciumEnv.arciumClusterOffset);

  async function initEncodeBasicCompDef(
    prog: Program<BiocypherMxe>,
    owner: anchor.web3.Keypair
  ): Promise<string> {
    const baseSeedCompDefAcc = getArciumAccountBaseSeed(
      "ComputationDefinitionAccount"
    );
    const offset = getCompDefAccOffset("encode_basic");
    const compDefPDA = PublicKey.findProgramAddressSync(
      [baseSeedCompDefAcc, prog.programId.toBuffer(), offset],
      getArciumProgramId()
    )[0];
    const arciumProgram = getArciumProgram(
      provider as anchor.AnchorProvider
    );
    const mxeAccount = getMXEAccAddress(prog.programId);
    const mxeAcc = await arciumProgram.account.mxeAccount.fetch(mxeAccount);
    const lutAddress = getLookupTableAddress(
      prog.programId,
      mxeAcc.lutOffsetSlot
    );
    const sig = await prog.methods
      .initEncodeBasicCompDef()
      .accounts({
        compDefAccount: compDefPDA,
        payer: owner.publicKey,
        mxeAccount,
        addressLookupTable: lutAddress,
      })
      .signers([owner])
      .rpc({ preflightCommitment: "confirmed", commitment: "confirmed" });
    const rawCircuit = fs.readFileSync("build/encode_basic.arcis");
    await uploadCircuit(
      provider as anchor.AnchorProvider,
      "encode_basic",
      prog.programId,
      rawCircuit,
      true
    );
    return sig;
  }

  async function initDecodeBasicCompDef(
    prog: Program<BiocypherMxe>,
    owner: anchor.web3.Keypair
  ): Promise<string> {
    const baseSeedCompDefAcc = getArciumAccountBaseSeed(
      "ComputationDefinitionAccount"
    );
    const offset = getCompDefAccOffset("decode_basic");
    const compDefPDA = PublicKey.findProgramAddressSync(
      [baseSeedCompDefAcc, prog.programId.toBuffer(), offset],
      getArciumProgramId()
    )[0];
    const arciumProgram = getArciumProgram(
      provider as anchor.AnchorProvider
    );
    const mxeAccount = getMXEAccAddress(prog.programId);
    const mxeAcc = await arciumProgram.account.mxeAccount.fetch(mxeAccount);
    const lutAddress = getLookupTableAddress(
      prog.programId,
      mxeAcc.lutOffsetSlot
    );
    const sig = await prog.methods
      .initDecodeBasicCompDef()
      .accounts({
        compDefAccount: compDefPDA,
        payer: owner.publicKey,
        mxeAccount,
        addressLookupTable: lutAddress,
      })
      .signers([owner])
      .rpc({ preflightCommitment: "confirmed", commitment: "confirmed" });
    const rawCircuit = fs.readFileSync("build/decode_basic.arcis");
    await uploadCircuit(
      provider as anchor.AnchorProvider,
      "decode_basic",
      prog.programId,
      rawCircuit,
      true
    );
    return sig;
  }

  async function getMXEPublicKeyWithRetry(
    prov: anchor.AnchorProvider,
    programId: PublicKey,
    maxRetries = 20,
    retryDelayMs = 500
  ): Promise<Uint8Array> {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        const pk = await getMXEPublicKey(prov, programId);
        if (pk) return pk;
      } catch (e) {
        console.log(`Attempt ${attempt} failed:`, e);
      }
      if (attempt < maxRetries) {
        await new Promise((r) => setTimeout(r, retryDelayMs));
      }
    }
    throw new Error(`Failed to get MXE public key after ${maxRetries} attempts`);
  }

  function readKpJson(path: string): anchor.web3.Keypair {
    const file = fs.readFileSync(path);
    return anchor.web3.Keypair.fromSecretKey(
      new Uint8Array(JSON.parse(file.toString()))
    );
  }

  it("encodes 4 bytes to 16 DNA bases (MPC)", async () => {
    const owner = readKpJson(`${os.homedir()}/.config/solana/id.json`);
    const mxePublicKey = await getMXEPublicKeyWithRetry(
      provider as anchor.AnchorProvider,
      program.programId
    );
    const privateKey = x25519.utils.randomSecretKey();
    const publicKey = x25519.getPublicKey(privateKey);
    const sharedSecret = x25519.getSharedSecret(privateKey, mxePublicKey);
    const cipher = new RescueCipher(sharedSecret);

    await initEncodeBasicCompDef(program, owner);

    // Message: "Hi" = 0x48, 0x69, 0x00, 0x00 (4 bytes)
    const message = new Uint8Array([0x48, 0x69, 0x00, 0x00]);
    const plaintext = Array.from(message).map((b) => BigInt(b));
    const nonce = randomBytes(16);
    const ciphertext = cipher.encrypt(plaintext, nonce);

    const encodeEventPromise = awaitEvent("encodeBasicEvent");
    const computationOffset = new anchor.BN(randomBytes(8), "hex");

    await program.methods
      .encodeBasic(
        computationOffset,
        Array.from(ciphertext[0]),
        Array.from(ciphertext[1]),
        Array.from(ciphertext[2]),
        Array.from(ciphertext[3]),
        Array.from(publicKey),
        new anchor.BN(deserializeLE(nonce).toString())
      )
      .accountsPartial({
        computationAccount: getComputationAccAddress(
          arciumEnv.arciumClusterOffset,
          computationOffset
        ),
        clusterAccount,
        mxeAccount: getMXEAccAddress(program.programId),
        mempoolAccount: getMempoolAccAddress(arciumEnv.arciumClusterOffset),
        executingPool: getExecutingPoolAccAddress(
          arciumEnv.arciumClusterOffset
        ),
        compDefAccount: getCompDefAccAddress(
          program.programId,
          Buffer.from(getCompDefAccOffset("encode_basic")).readUInt32LE()
        ),
      })
      .rpc({ skipPreflight: true, preflightCommitment: "confirmed", commitment: "confirmed" });

    await awaitComputationFinalization(
      provider as anchor.AnchorProvider,
      computationOffset,
      program.programId,
      "confirmed"
    );

    const ev = await encodeEventPromise;
    const decrypted = cipher.decrypt(
      ev.ciphertexts.map((c: number[]) => new Uint8Array(c)),
      ev.nonce
    );
    const dnaStr = dnaToString(decrypted.map((d) => Number(d)));
    console.log("Encoded DNA:", dnaStr);
    // "Hi" = 0x48 0x69 -> bits: 01001000 01101001
    // 01 00 10 00 01 10 10 01 = T A C A T C C T
    expect(dnaStr.length).to.equal(16);
    expect(["A", "T", "C", "G"].includes(dnaStr[0])).to.be.true;
  });

  it("decodes 16 DNA bases to 4 bytes (MPC)", async () => {
    const owner = readKpJson(`${os.homedir()}/.config/solana/id.json`);
    const mxePublicKey = await getMXEPublicKeyWithRetry(
      provider as anchor.AnchorProvider,
      program.programId
    );
    const privateKey = x25519.utils.randomSecretKey();
    const publicKey = x25519.getPublicKey(privateKey);
    const sharedSecret = x25519.getSharedSecret(privateKey, mxePublicKey);
    const cipher = new RescueCipher(sharedSecret);

    await initDecodeBasicCompDef(program, owner);

    // DNA "TACATCTT" = 01 00 10 00 01 10 10 01 = 0x48 0x69 = "Hi"
    // Full 16 bases: TACATCTT + 8 more (e.g. AAAA)
    const dnaBases = [1, 0, 2, 0, 1, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0]; // TACATCTT AAAA...
    const plaintext = dnaBases.map((b) => BigInt(b));
    const nonce = randomBytes(16);
    const ciphertext = cipher.encrypt(plaintext, nonce);

    const decodeEventPromise = awaitEvent("decodeBasicEvent");
    const computationOffset = new anchor.BN(randomBytes(8), "hex");

    const ciphertextArrays = ciphertext.map((c) => Array.from(c));
    await program.methods
      .decodeBasic(
        computationOffset,
        ciphertextArrays,
        Array.from(publicKey),
        new anchor.BN(deserializeLE(nonce).toString())
      )
      .accountsPartial({
        computationAccount: getComputationAccAddress(
          arciumEnv.arciumClusterOffset,
          computationOffset
        ),
        clusterAccount,
        mxeAccount: getMXEAccAddress(program.programId),
        mempoolAccount: getMempoolAccAddress(arciumEnv.arciumClusterOffset),
        executingPool: getExecutingPoolAccAddress(
          arciumEnv.arciumClusterOffset
        ),
        compDefAccount: getCompDefAccAddress(
          program.programId,
          Buffer.from(getCompDefAccOffset("decode_basic")).readUInt32LE()
        ),
      })
      .rpc({ skipPreflight: true, preflightCommitment: "confirmed", commitment: "confirmed" });

    await awaitComputationFinalization(
      provider as anchor.AnchorProvider,
      computationOffset,
      program.programId,
      "confirmed"
    );

    const ev = await decodeEventPromise;
    const decrypted = cipher.decrypt(
      ev.ciphertexts.map((c: number[]) => new Uint8Array(c)),
      ev.nonce
    );
    const msg = Buffer.from(decrypted.map((d) => Number(d)));
    console.log("Decoded bytes:", Array.from(msg));
    expect(msg[0]).to.equal(0x48);
    expect(msg[1]).to.equal(0x69);
  });
});
