/**
 * Arcium MPC client for Bi0cyph3r encode_basic / decode_basic.
 * Uses Solana CLI keypair (~/.config/solana/id.json).
 */

import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { PublicKey } from "@solana/web3.js";
import { randomBytes } from "crypto";
import * as fs from "fs";
import * as path from "path";
import {
  awaitComputationFinalization,
  getArciumEnv,
  getCompDefAccOffset,
  getMXEAccAddress,
  getMempoolAccAddress,
  getCompDefAccAddress,
  getExecutingPoolAccAddress,
  getComputationAccAddress,
  getMXEPublicKey,
  getClusterAccAddress,
  RescueCipher,
  deserializeLE,
  x25519,
} from "@arcium-hq/client";

const DNA_BASES = ["A", "T", "C", "G"];
const DNA_TO_INDEX: Record<string, number> = { A: 0, T: 1, C: 2, G: 3 };

function dnaToString(dnaBytes: number[]): string {
  return dnaBytes.map((b) => DNA_BASES[b & 3]).join("");
}

function stringToDnaBases(s: string): number[] {
  const out: number[] = [];
  for (const c of s.toUpperCase()) {
    const idx = DNA_TO_INDEX[c];
    if (idx === undefined) throw new Error(`Invalid DNA base: ${c}`);
    out.push(idx);
  }
  return out;
}

function readKeypair(p: string): anchor.web3.Keypair {
  const resolved = p.startsWith("~")
    ? path.join(process.env.HOME || "", p.slice(1))
    : path.resolve(p);
  const file = fs.readFileSync(resolved);
  return anchor.web3.Keypair.fromSecretKey(
    new Uint8Array(JSON.parse(file.toString()))
  );
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
      console.warn(`MXE public key attempt ${attempt} failed:`, e);
    }
    if (attempt < maxRetries) {
      await new Promise((r) => setTimeout(r, retryDelayMs));
    }
  }
  throw new Error(`Failed to get MXE public key after ${maxRetries} attempts`);
}

export interface ArciumClientConfig {
  rpcUrl: string;
  keypairPath: string;
  mxePath: string;
  programId: string;
}

export interface EncodeResult {
  dna_sequence: string;
  length: number;
  gc_content: number;
}

export interface DecodeResult {
  decoded_message: string;
}

export class ArciumClient {
  private program!: Program;
  private provider!: anchor.AnchorProvider;
  private programId!: PublicKey;
  private clientPublicKey!: Uint8Array;
  private cipher!: RescueCipher;
  private initPromise: Promise<void> | null = null;

  constructor(private config: ArciumClientConfig) {}

  async ready(): Promise<void> {
    return this.ensureInit();
  }

  private async ensureInit(): Promise<void> {
    if (this.initPromise) return this.initPromise;

    this.initPromise = (async () => {
      process.chdir(this.config.mxePath);
      const keypair = readKeypair(this.config.keypairPath);
      const connection = new anchor.web3.Connection(this.config.rpcUrl, "confirmed");
      const wallet = new anchor.Wallet(keypair);
      this.provider = new anchor.AnchorProvider(connection, wallet, {
        preflightCommitment: "confirmed",
        commitment: "confirmed",
      });
      anchor.setProvider(this.provider);

      const idlPath = path.join(
        this.config.mxePath,
        "target",
        "idl",
        "biocypher_mxe.json"
      );
      if (!fs.existsSync(idlPath)) {
        throw new Error(
          `IDL not found at ${idlPath}. Run "cd biocypher-mxe && arcium build" first.`
        );
      }
      const idl = JSON.parse(fs.readFileSync(idlPath, "utf-8"));
      this.programId = new PublicKey(this.config.programId);
      this.program = new Program(idl, this.provider);

      const mxePublicKey = await getMXEPublicKeyWithRetry(
        this.provider,
        this.programId
      );
      const privateKey = x25519.utils.randomSecretKey();
      this.clientPublicKey = x25519.getPublicKey(privateKey);
      const sharedSecret = x25519.getSharedSecret(privateKey, mxePublicKey);
      this.cipher = new RescueCipher(sharedSecret);
    })();

    return this.initPromise;
  }

  async encode(message: string): Promise<EncodeResult> {
    await this.ensureInit();

    if (message.length > 4) {
      throw new Error("Arcium encode_basic supports max 4 bytes. Truncating or use local encode.");
    }

    const bytes = new Uint8Array(4);
    const encoder = new TextEncoder();
    const encoded = encoder.encode(message);
    for (let i = 0; i < Math.min(4, encoded.length); i++) bytes[i] = encoded[i];

    const plaintext = Array.from(bytes).map((b) => BigInt(b));
    const nonce = randomBytes(16);
    const ciphertext = this.cipher.encrypt(plaintext, nonce);

    const arciumEnv = getArciumEnv();
    const clusterAccount = getClusterAccAddress(arciumEnv.arciumClusterOffset);
    const computationOffset = new anchor.BN(randomBytes(8), "hex");

    const encodeEventPromise = new Promise<{ ciphertexts: number[][]; nonce: number[] }>((res) => {
      const listenerId = this.program.addEventListener("encodeBasicEvent", (ev: unknown) => {
        this.program.removeEventListener(listenerId);
        res(ev as { ciphertexts: number[][]; nonce: number[] });
      });
    });

    await this.program.methods
      .encodeBasic(
        computationOffset,
        Array.from(ciphertext[0]),
        Array.from(ciphertext[1]),
        Array.from(ciphertext[2]),
        Array.from(ciphertext[3]),
        Array.from(this.clientPublicKey),
        new anchor.BN(deserializeLE(nonce).toString())
      )
      .accountsPartial({
        computationAccount: getComputationAccAddress(
          arciumEnv.arciumClusterOffset,
          computationOffset
        ),
        clusterAccount,
        mxeAccount: getMXEAccAddress(this.programId),
        mempoolAccount: getMempoolAccAddress(arciumEnv.arciumClusterOffset),
        executingPool: getExecutingPoolAccAddress(
          arciumEnv.arciumClusterOffset
        ),
        compDefAccount: getCompDefAccAddress(
          this.programId,
          Buffer.from(getCompDefAccOffset("encode_basic")).readUInt32LE()
        ),
      })
      .rpc({ skipPreflight: true, preflightCommitment: "confirmed", commitment: "confirmed" });

    await awaitComputationFinalization(
      this.provider,
      computationOffset,
      this.programId,
      "confirmed"
    );

    const ev = await encodeEventPromise;
    const decrypted = this.cipher.decrypt(
      ev.ciphertexts.map((c) => Array.from(c)),
      new Uint8Array(ev.nonce)
    );
    const dnaStr = dnaToString(decrypted.map((d) => Number(d)));

    let gc = 0;
    for (const c of dnaStr) if (c === "G" || c === "C") gc++;
    const gcContent = (gc / dnaStr.length) * 100;

    return {
      dna_sequence: dnaStr,
      length: dnaStr.length,
      gc_content: Math.round(gcContent * 10) / 10,
    };
  }

  async decode(sequence: string): Promise<DecodeResult> {
    await this.ensureInit();

    const cleaned = sequence.replace(/\s/g, "").toUpperCase();
    if (cleaned.length !== 16) {
      throw new Error("Arcium decode_basic requires exactly 16 DNA bases.");
    }

    const dnaBases = stringToDnaBases(cleaned);
    const plaintext = dnaBases.map((b) => BigInt(b));
    const nonce = randomBytes(16);
    const ciphertext = this.cipher.encrypt(plaintext, nonce);

    const arciumEnv = getArciumEnv();
    const clusterAccount = getClusterAccAddress(arciumEnv.arciumClusterOffset);
    const computationOffset = new anchor.BN(randomBytes(8), "hex");

    const decodeEventPromise = new Promise<{ ciphertexts: number[][]; nonce: number[] }>((res) => {
      const listenerId = this.program.addEventListener("decodeBasicEvent", (ev: unknown) => {
        this.program.removeEventListener(listenerId);
        res(ev as { ciphertexts: number[][]; nonce: number[] });
      });
    });
    const ciphertextArrays = ciphertext.map((c) => Array.from(c));

    await this.program.methods
      .decodeBasic(
        computationOffset,
        ciphertextArrays,
        Array.from(this.clientPublicKey),
        new anchor.BN(deserializeLE(nonce).toString())
      )
      .accountsPartial({
        computationAccount: getComputationAccAddress(
          arciumEnv.arciumClusterOffset,
          computationOffset
        ),
        clusterAccount,
        mxeAccount: getMXEAccAddress(this.programId),
        mempoolAccount: getMempoolAccAddress(arciumEnv.arciumClusterOffset),
        executingPool: getExecutingPoolAccAddress(
          arciumEnv.arciumClusterOffset
        ),
        compDefAccount: getCompDefAccAddress(
          this.programId,
          Buffer.from(getCompDefAccOffset("decode_basic")).readUInt32LE()
        ),
      })
      .rpc({ skipPreflight: true, preflightCommitment: "confirmed", commitment: "confirmed" });

    await awaitComputationFinalization(
      this.provider,
      computationOffset,
      this.programId,
      "confirmed"
    );

    const ev = await decodeEventPromise;
    const decrypted = this.cipher.decrypt(
      ev.ciphertexts.map((c) => Array.from(c)),
      new Uint8Array(ev.nonce)
    );
    const msg = Buffer.from(decrypted.map((d) => Number(d)));
    const decoded = new TextDecoder().decode(msg).replace(/\0/g, "");

    return { decoded_message: decoded };
  }
}
