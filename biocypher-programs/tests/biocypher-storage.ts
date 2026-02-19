import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { BiocypherStorage } from "../target/types/biocypher_storage";

describe("biocypher-storage", () => {
  anchor.setProvider(anchor.AnchorProvider.env());

  const program = (anchor.workspace as any).biocypherStorage as Program<BiocypherStorage>;

  it("records encode attestation", async () => {
    const sequenceHash = Buffer.alloc(32, 1);
    const tx = await program.methods
      .recordEncode(0, Array.from(sequenceHash), new anchor.BN(Date.now() / 1000))
      .rpc();
    expect(tx).toBeDefined();
  });

  it("records decode attestation", async () => {
    const sequenceHash = Buffer.alloc(32, 2);
    const tx = await program.methods
      .recordDecode(0, Array.from(sequenceHash), new anchor.BN(Date.now() / 1000))
      .rpc();
    expect(tx).toBeDefined();
  });

  it("records safety attestation", async () => {
    const sequenceHash = Buffer.alloc(32, 3);
    const tx = await program.methods
      .recordSafety(Array.from(sequenceHash), 0, new anchor.BN(Date.now() / 1000))
      .rpc();
    expect(tx).toBeDefined();
  });
});
