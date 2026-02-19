/**
 * Bi0cyph3r Arcium MPC Service
 *
 * HTTP API for Arcium encode_basic / decode_basic.
 * Secure transmission of plasmid designs to DNA manufacturers (Twist, IDT, etc.).
 * Uses Solana CLI keypair (~/.config/solana/id.json).
 * Run from repo root; service must find biocypher-mxe for Arcium config.
 */

import express from "express";
import cors from "cors";
import * as path from "path";
import { randomUUID } from "crypto";
import { ArciumClient } from "./arcium-client.js";

const PORT = parseInt(process.env.ARCIUM_SERVICE_PORT || "3001", 10);
const RPC_URL = process.env.RPC_URL || "http://127.0.0.1:8899";
const KEYPAIR_PATH = process.env.KEYPAIR_PATH || "~/.config/solana/id.json";
const MXE_PATH = process.env.MXE_PATH || process.cwd();
const PROGRAM_ID = process.env.MXE_PROGRAM_ID || "EneGTgWJJwnxLeBkD128NtpuGQVCmq14cUnPCNEVyueE";
const MANUFACTURER_API_URL = process.env.MANUFACTURER_API_URL || "";
const TRANSMIT_MOCK = process.env.TRANSMIT_MOCK === "true";
const USE_BUILTIN_MOCK = process.env.USE_BUILTIN_MOCK === "true";

/** In-memory key escrow store: transmission_id -> { k2, owner_id?, expires_at? } */
const escrowStore = new Map<
  string,
  { k2: string; owner_id?: string; expires_at?: number }
>();

const client = new ArciumClient({
  rpcUrl: RPC_URL,
  keypairPath: KEYPAIR_PATH,
  mxePath: MXE_PATH,
  programId: PROGRAM_ID,
});

const app = express();
app.use(cors());
app.use(express.json());

app.get("/health", (_req, res) => {
  res.json({
    status: "ok",
    service: "biocypher-arcium-service",
    rpc: RPC_URL,
    mxe_path: MXE_PATH,
  });
});

app.get("/status", async (_req, res) => {
  try {
    await client.ready();
    res.json({
      status: "connected",
      arcium: "ready",
      message: "Arcium MPC encryption available",
    });
  } catch (e) {
    res.status(503).json({
      status: "unavailable",
      arcium: "not_ready",
      error: e instanceof Error ? e.message : String(e),
    });
  }
});

app.post("/encode-mpc", async (req, res) => {
  try {
    const { message } = req.body;
    if (typeof message !== "string") {
      res.status(400).json({ error: "message (string) required" });
      return;
    }
    if (message.length > 4) {
      res.status(400).json({
        error: "Arcium encode_basic supports max 4 bytes. Use local encode for longer messages.",
      });
      return;
    }
    const result = await client.encode(message);
    res.json({
      dna_sequence: result.dna_sequence,
      stats: {
        length: result.length,
        gc_content: result.gc_content,
      },
      source: "arcium",
    });
  } catch (e) {
    console.error("encode-mpc error:", e);
    res.status(500).json({
      error: e instanceof Error ? e.message : String(e),
    });
  }
});

app.post("/decode-mpc", async (req, res) => {
  try {
    const { sequence } = req.body;
    if (typeof sequence !== "string") {
      res.status(400).json({ error: "sequence (string) required" });
      return;
    }
    const cleaned = sequence.replace(/\s/g, "");
    if (cleaned.length !== 16) {
      res.status(400).json({
        error: "Arcium decode_basic requires exactly 16 DNA bases.",
      });
      return;
    }
    const result = await client.decode(cleaned);
    res.json({
      decoded_message: result.decoded_message,
      source: "arcium",
    });
  } catch (e) {
    console.error("decode-mpc error:", e);
    res.status(500).json({
      error: e instanceof Error ? e.message : String(e),
    });
  }
});

/**
 * Key escrow: store K2 for split-key mode.
 * Body: { transmission_id, k2, owner_id?, expires_at? }
 */
app.post("/escrow-store", (req, res) => {
  try {
    const { transmission_id, k2, owner_id, expires_at } = req.body;
    if (typeof transmission_id !== "string" || !transmission_id.trim()) {
      res.status(400).json({ error: "transmission_id (string) required" });
      return;
    }
    if (typeof k2 !== "string" || !k2.trim()) {
      res.status(400).json({ error: "k2 (string, base64) required" });
      return;
    }
    try {
      const decoded = Buffer.from(k2, "base64");
      if (decoded.length !== 32) {
        res.status(400).json({ error: "k2 must decode to 32 bytes" });
        return;
      }
    } catch {
      res.status(400).json({ error: "k2 must be valid base64" });
      return;
    }
    const expiresAt =
      typeof expires_at === "string" && expires_at
        ? new Date(expires_at).getTime()
        : undefined;
    escrowStore.set(transmission_id.trim(), {
      k2: k2.trim(),
      owner_id: typeof owner_id === "string" ? owner_id : undefined,
      expires_at: expiresAt,
    });
    res.json({ stored: true, transmission_id: transmission_id.trim() });
  } catch (e) {
    console.error("escrow-store error:", e);
    res.status(500).json({
      error: e instanceof Error ? e.message : String(e),
    });
  }
});

/**
 * Key escrow: retrieve K2 by transmission_id.
 * Body: { transmission_id, owner_id? }
 */
app.post("/escrow-retrieve", (req, res) => {
  try {
    const { transmission_id, owner_id } = req.body;
    if (typeof transmission_id !== "string" || !transmission_id.trim()) {
      res.status(400).json({ error: "transmission_id (string) required" });
      return;
    }
    const entry = escrowStore.get(transmission_id.trim());
    if (!entry) {
      res.status(404).json({ error: "transmission_id not found" });
      return;
    }
    if (entry.expires_at && Date.now() > entry.expires_at) {
      escrowStore.delete(transmission_id.trim());
      res.status(404).json({ error: "transmission expired" });
      return;
    }
    if (entry.owner_id && typeof owner_id === "string" && entry.owner_id !== owner_id) {
      res.status(403).json({ error: "owner_id mismatch" });
      return;
    }
    res.json({ k2: entry.k2 });
  } catch (e) {
    console.error("escrow-retrieve error:", e);
    res.status(500).json({
      error: e instanceof Error ? e.message : String(e),
    });
  }
});

/**
 * Transmit split-key plasmid: send FASTA directly to manufacturer (no encryption).
 * The DNA sequence encodes ciphertext; manufacturer has no key.
 * Body: { fasta, instructions?, manufacturer_url? }
 */
app.post("/transmit-split-key", async (req, res) => {
  try {
    const { fasta, instructions, manufacturer_url } = req.body;
    if (typeof fasta !== "string" || !fasta.trim()) {
      res.status(400).json({ error: "fasta (string) required" });
      return;
    }
    let targetUrl = (manufacturer_url || MANUFACTURER_API_URL).trim();
    if (USE_BUILTIN_MOCK && !manufacturer_url) {
      targetUrl = `http://127.0.0.1:${PORT}/transmit-receive`;
    }
    const transmissionId = randomUUID();
    const payload = {
      transmission_id: transmissionId,
      fasta: fasta.trim(),
      instructions: instructions ?? null,
      source: "biocypher-split-key",
      timestamp: new Date().toISOString(),
    };

    if ((!targetUrl && !USE_BUILTIN_MOCK) || TRANSMIT_MOCK) {
      if (TRANSMIT_MOCK || !targetUrl) {
        console.log("[transmit-split-key] Transmission received (mock/staging)", transmissionId);
      }
      res.json({
        message: TRANSMIT_MOCK
          ? "Split-key transmission accepted (mock mode)"
          : "Split-key transmission accepted. Set MANUFACTURER_API_URL or provide manufacturer_url for production.",
        transmission_id: transmissionId,
      });
      return;
    }

    const fwd = await fetch(targetUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!fwd.ok) {
      const errText = await fwd.text();
      res.status(502).json({
        error: `Manufacturer API error (${fwd.status}): ${errText}`,
        transmission_id: transmissionId,
      });
      return;
    }
    const fwdJson = await fwd.json().catch(() => ({}));
    res.json({
      message: "Split-key transmission sent to manufacturer",
      transmission_id: transmissionId,
      manufacturer_response: fwdJson,
    });
  } catch (e) {
    console.error("transmit-split-key error:", e);
    res.status(500).json({
      error: e instanceof Error ? e.message : String(e),
    });
  }
});

/**
 * Mock manufacturer receiver endpoint.
 * Accepts encrypted transmissions for testing. Logs transmission_id and encrypted blob length.
 */
app.post("/transmit-receive", (req, res) => {
  const { transmission_id, encrypted, source, timestamp } = req.body;
  const encLen = typeof encrypted === "string" ? encrypted.length : 0;
  console.log("[transmit-receive] Received transmission", {
    transmission_id: transmission_id || "(none)",
    encrypted_length: encLen,
    source: source || "(none)",
    timestamp: timestamp || "(none)",
  });
  res.json({
    received: true,
    transmission_id: transmission_id || randomUUID(),
  });
});

/**
 * Secure transmission endpoint.
 * Forwards encrypted plasmid FASTA + instructions to DNA manufacturer API.
 * Payload stays encrypted end-to-end; manufacturer decrypts with shared password.
 *
 * Encryption format (AES-256-GCM, PBKDF2-SHA256 100k iterations):
 *   encrypted = base64(salt(16) || iv(12) || ciphertext+tag)
 *   Key derived from password + salt.
 */
app.post("/transmit-secure", async (req, res) => {
  try {
    const { encrypted, manufacturer_url } = req.body;
    if (typeof encrypted !== "string") {
      res.status(400).json({ error: "encrypted (string) required" });
      return;
    }
    let targetUrl = (manufacturer_url || MANUFACTURER_API_URL).trim();
    if (USE_BUILTIN_MOCK && !manufacturer_url) {
      targetUrl = `http://127.0.0.1:${PORT}/transmit-receive`;
    }
    const transmissionId = randomUUID();
    const payload = {
      transmission_id: transmissionId,
      encrypted,
      source: "biocypher-arcium",
      timestamp: new Date().toISOString(),
    };

    if ((!targetUrl && !USE_BUILTIN_MOCK) || TRANSMIT_MOCK) {
      if (TRANSMIT_MOCK || !targetUrl) {
        console.log("[transmit-secure] Transmission received (mock/staging)", transmissionId);
      }
      res.json({
        message: TRANSMIT_MOCK
          ? "Encrypted transmission accepted (mock mode)"
          : "Encrypted transmission accepted. Set MANUFACTURER_API_URL or provide manufacturer_url for production.",
        transmission_id: transmissionId,
      });
      return;
    }

    const fwd = await fetch(targetUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!fwd.ok) {
      const errText = await fwd.text();
      res.status(502).json({
        error: `Manufacturer API error (${fwd.status}): ${errText}`,
        transmission_id: transmissionId,
      });
      return;
    }
    const fwdJson = await fwd.json().catch(() => ({}));
    res.json({
      message: "Encrypted transmission sent to manufacturer",
      transmission_id: transmissionId,
      manufacturer_response: fwdJson,
    });
  } catch (e) {
    console.error("transmit-secure error:", e);
    res.status(500).json({
      error: e instanceof Error ? e.message : String(e),
    });
  }
});

app.listen(PORT, () => {
  console.log(`🧬 Bi0cyph3r Arcium Service listening on http://127.0.0.1:${PORT}`);
  console.log(`   RPC: ${RPC_URL}`);
  console.log(`   MXE: ${MXE_PATH}`);
  console.log(`   Health: http://127.0.0.1:${PORT}/health`);
  console.log(`   Status: http://127.0.0.1:${PORT}/status`);
});
