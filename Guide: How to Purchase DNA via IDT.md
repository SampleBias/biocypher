# Guide: How to Purchase DNA via IDT

---

## Prerequisites

- A Bi0cyph3r-generated DNA sequence
- Safety Screener result: ✅ SAFE
- Knowledge of sequence length
- Institutional approval (if required)

---

## Step 1 — Generate DNA via Bi0cyph3r

Use CLI or Web UI:

```bash
bi0cyph3r encode "Hello World"
```

Or via API:

```bash
curl -X POST http://127.0.0.1:8080/api/encode \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello World","mode":"basic"}'
```

Example output:

```
ATTTTTTTCGTCACCGAATCAGTTGGGTCAAAGGGAGCAGTTTAGTTTTGCCCGGTCTAAATTGGGTTTTAAACC
```

---

## Step 2 — Run Safety Screening (Mandatory)

```bash
bi0cyph3r safety "ATTTTTTTCGTCACCGAATCAG..."
```

Or via API:

```bash
curl -X POST http://127.0.0.1:8080/api/safety-screen \
  -H "Content-Type: application/json" \
  -d '{"dna_sequence":"ATCGATCGATCG"}'
```

The screener evaluates:

- Pathogen/toxin signatures
- Human and *E. coli* similarity
- GC content and homopolymer runs
- ORF and structural anomalies
- Risk classification (Safe / Caution / Unsafe)

Only proceed if result = ✅ SAFE.

---

## Step 3 — Determine Appropriate IDT Product

| Sequence Length | Recommended Product |
|-----------------|--------------------|
| < 200 bp        | Custom DNA Oligos  |
| 125–3000 bp     | gBlocks Gene Fragments |

### IDT Product Pages

- Custom DNA Oligos  
  https://www.idtdna.com/pages/products/dna/custom-dna-oligos

- gBlocks Gene Fragments  
  https://www.idtdna.com/pages/products/dna/fragments/gblocks-gene-fragments

---

## Step 4 — Prepare Sequence for Submission

Before submitting:

- Sequence must contain only A, T, C, G
- Uppercase recommended
- No ambiguous bases (N, R, Y, etc.)
- Avoid long homopolymers (Nanopore mode minimizes this)
- Confirm GC content is within reasonable synthesis bounds (40–60% ideal)

For gBlocks:

- Double-stranded format
- Between 125–3000 bp
- Valid IUPAC nucleotide alphabet

---

## Step 5 — Order via IDT

1. Log into https://www.idtdna.com
2. Select appropriate product (Oligo or gBlock)
3. Paste DNA sequence
4. Name the sequence
5. Choose synthesis scale (e.g., 25 nmol for short tests)
6. Select purification:
   - Standard Desalt (default)
   - HPLC (if higher purity required)
7. Select format (dry or solution)
8. Review order
9. Submit

Vendor screening will independently evaluate sequence risk.

---

## Security Boundary Reminder

Physical synthesis does not weaken cryptographic protections, but it introduces real-world biosafety considerations.
