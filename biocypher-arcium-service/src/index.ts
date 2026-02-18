/**
 * Bi0cyph3r Arcium MPC Service
 *
 * HTTP API for Arcium encode_basic / decode_basic.
 * Uses Solana CLI keypair (~/.config/solana/id.json).
 * Run from repo root; service must find biocypher-mxe for Arcium config.
 */

import express from "express";
import cors from "cors";
import * as path from "path";
import { ArciumClient } from "./arcium-client.js";

const PORT = parseInt(process.env.ARCIUM_SERVICE_PORT || "3001", 10);
const RPC_URL = process.env.RPC_URL || "http://127.0.0.1:8899";
const KEYPAIR_PATH = process.env.KEYPAIR_PATH || "~/.config/solana/id.json";
const MXE_PATH = process.env.MXE_PATH || process.cwd();
const PROGRAM_ID = process.env.MXE_PROGRAM_ID || "BioCyphMXE11111111111111111111111111111111";

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

app.listen(PORT, () => {
  console.log(`🧬 Bi0cyph3r Arcium Service listening on http://127.0.0.1:${PORT}`);
  console.log(`   RPC: ${RPC_URL}`);
  console.log(`   MXE: ${MXE_PATH}`);
  console.log(`   Health: http://127.0.0.1:${PORT}/health`);
  console.log(`   Status: http://127.0.0.1:${PORT}/status`);
});
