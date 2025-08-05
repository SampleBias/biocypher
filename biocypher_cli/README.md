# 🧬 BioCypher CLI - Advanced DNA Cryptography System

A powerful command-line tool for encoding text messages into DNA sequences and decoding them back, with multiple encoding modes and advanced features.

## ✨ Features

- **Multiple Encoding Modes**:
  - 🧬 **Basic**: Simple binary-to-DNA mapping (A=00, T=01, C=10, G=11)
  - 🔬 **Nanopore**: Optimized for nanopore sequencing with error correction
  - 🔐 **Secure**: AES-256-CBC encryption + DNA encoding with password protection

- **Advanced Analysis**:
  - 📊 DNA sequence statistics and composition analysis
  - 🛡️ Safety screening for pathogen signatures
  - 🔍 Nanopore sequencing optimization assessment

- **Beautiful Output**:
  - 🌈 Colored DNA sequences (A=red, T=blue, C=green, G=yellow)
  - 📋 Rich formatted tables and reports
  - 📈 Progress bars for long operations

- **Flexible I/O**:
  - 📁 File input/output support (text, FASTA, JSON formats)
  - 🔄 Auto-detection of encoding modes
  - 📝 Batch processing capabilities

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
cd biocypher_cli
pip install -r requirements.txt
```

### Make Executable

```bash
chmod +x biocypher_cli.py
```

### Optional: Install System-wide

```bash
pip install -e .
```

After installation, you can use `biocypher` command from anywhere.

## 🎯 Quick Start

### Basic Usage

```bash
# Encode a message
./biocypher_cli.py encode "Hello World"

# Decode a DNA sequence  
./biocypher_cli.py decode "ATCGATCGTACG..."

# Analyze a DNA sequence
./biocypher_cli.py analyze "ATCGATCGTACG..."
```

### Advanced Examples

```bash
# Nanopore-optimized encoding
./biocypher_cli.py encode -m nanopore "My secret message"

# Secure mode with password
./biocypher_cli.py encode -m secure -p mypassword "Top secret data"

# File input/output
./biocypher_cli.py encode -i message.txt -o sequence.dna

# Safety screening
./biocypher_cli.py safety "ATCGATCGTACG..."

# Generate secure passwords
./biocypher_cli.py password generate -l 16 -c 3
```

## 📖 Command Reference

### Main Commands

#### `encode` - Encode text to DNA

```bash
biocypher encode [OPTIONS] [MESSAGE]

Options:
  -m, --mode [basic|nanopore|secure]  Encoding mode (default: basic)
  -i, --input-file PATH               Read message from file
  -o, --output-file PATH              Write DNA sequence to file
  -p, --password TEXT                 Password for secure mode
  --error-correction / --no-error-correction  Enable error correction (default: on)
  --format [text|fasta|json]          Output format (default: text)
  --show-stats                        Show sequence statistics
```

#### `decode` - Decode DNA to text

```bash
biocypher decode [OPTIONS] [SEQUENCE]

Options:
  -m, --mode [basic|nanopore|secure|auto]  Decoding mode (default: auto)
  -i, --input-file PATH               Read DNA sequence from file
  -o, --output-file PATH              Write decoded message to file
  -p, --password TEXT                 Password for secure mode
  --error-correction / --no-error-correction  Enable error correction (default: on)
  --show-stats                        Show sequence statistics
```

#### `analyze` - Analyze DNA sequence

```bash
biocypher analyze [OPTIONS] [SEQUENCE]

Options:
  -i, --input-file PATH               Read DNA sequence from file
  -m, --mode [basic|nanopore]         Analysis mode (default: nanopore)
```

#### `safety` - Safety screening

```bash
biocypher safety [OPTIONS] [SEQUENCE]

Options:
  -i, --input-file PATH               Read DNA sequence from file
```

#### `password` - Password utilities

```bash
# Generate secure passwords
biocypher password generate -l 16 -c 3

# Check password strength
biocypher password check mypassword123
```

#### `validate` - Validate DNA sequence

```bash
biocypher validate [OPTIONS] [SEQUENCE]

Options:
  -i, --input-file PATH               Read DNA sequence from file
```

### Global Options

```bash
Options:
  --version                   Show version
  -c, --config PATH          Configuration file path
  -v, --verbose              Enable verbose output
  --help                     Show help message
```

## 🔧 Configuration

BioCypher CLI supports configuration files for default settings:

### Configuration File Locations

1. `~/.biocypher.yaml` (preferred)
2. `~/.biocypher.yml`
3. `~/.config/biocypher/config.yaml`
4. `./biocypher.yaml` (current directory)

### Example Configuration

```yaml
# BioCypher CLI Configuration

# Processing limits
max_message_length: 1000
max_dna_sequence_length: 10000

# Default modes
default_encoding_mode: basic
default_output_format: text

# Security settings
password_min_length: 8
require_strong_passwords: true

# Display settings
colors_enabled: true
progress_bars: true
line_length: 60

# File processing
auto_detect_format: true
backup_files: false
```

## 🧬 Encoding Modes Explained

### Basic Mode
- Simple 2-bit binary to DNA mapping
- Fast and straightforward
- Best for: Simple text encoding

### Nanopore Mode
- Optimized for nanopore sequencing
- Avoids homopolymer runs (AAAA, TTTT, etc.)
- Balanced GC content
- Error correction with parity bits
- Best for: DNA synthesis and sequencing

### Secure Mode
- AES-256-CBC encryption
- PBKDF2 key derivation (100,000 iterations)
- Cryptographically secure
- Best for: Sensitive data protection

## 🛡️ Safety Features

BioCypher includes comprehensive safety screening:

- **Pathogen Signature Detection**: Identifies potential harmful sequences
- **Natural Sequence Matching**: Detects sequences from known organisms
- **Sequence Analysis**: Finds ORFs, homopolymers, and repetitive elements
- **Safety Recommendations**: Provides actionable guidance

## 📊 Output Examples

### DNA Sequence Display
```
🧬 Encoded DNA Sequence:
ATCG ATCG TACG TACG ATCG TACG ATCG TACG
TACG ATCG TACG ATCG TACG ATCG TACG ATCG
```

### Statistics Table
```
┌─────────────────┬─────────┐
│     Property    │  Value  │
├─────────────────┼─────────┤
│ Length          │ 64 bases│
│ A (Adenine)     │ 16      │
│ T (Thymine)     │ 16      │
│ C (Cytosine)    │ 16      │
│ G (Guanine)     │ 16      │
│ GC Content      │ 50.0%   │
└─────────────────┴─────────┘
```

### Safety Report
```
🧬 DNA Safety Screening Report
┌─────────────────────────────────────┐
│ ✅ Safety Status: SAFE              │
└─────────────────────────────────────┘

✅ No pathogen signatures detected
✅ No natural genome matches found
```

## 🔒 Security Notes

- Passwords are never stored or logged
- Secure password input (hidden typing)
- Strong password validation
- Cryptographically secure random generation
- Side-channel attack resistant key derivation

## 🐛 Troubleshooting

### Common Issues

1. **"Invalid DNA sequence"**
   - Ensure sequence contains only A, T, C, G characters
   - Check for proper formatting

2. **"Password required"**
   - Secure mode requires a password
   - Use `-p` option or enter when prompted

3. **"Decoding failed"**
   - Verify the correct encoding mode
   - Try auto-detection with `-m auto`

### Verbose Mode

For detailed error information:
```bash
biocypher -v encode "test message"
```

## 📚 Examples Collection

### File Processing
```bash
# Encode file with nanopore optimization
biocypher encode -m nanopore -i document.txt -o encoded.dna --show-stats

# Decode with auto-detection
biocypher decode -i encoded.dna -o decoded.txt

# Batch analysis
biocypher analyze -i sequences.fasta > analysis_report.txt
```

### Secure Operations
```bash
# Secure encoding with strong password
biocypher encode -m secure "Confidential data" -p "MyStr0ng!Pass"

# Generate and use secure password
PASSWORD=$(biocypher password generate -l 20)
biocypher encode -m secure -p "$PASSWORD" "Secret message"
```

### Safety Screening
```bash
# Screen a synthetic sequence
biocypher safety "ATGAAGCTGTATGACCCGATATCGATCG"

# Screen sequences from file
biocypher safety -i synthetic_constructs.fasta
```

## 🤝 Contributing

Contributions are welcome! Please ensure:

1. Code follows existing style
2. All tests pass
3. New features include tests
4. Documentation is updated

## 📄 License

This project is licensed under the bi0cyph3r DNA Cryptography System License. See LICENSE file for details.

## 👨‍💻 Author

James Utley - Advanced DNA Cryptography System

---

🧬 **BioCypher CLI** - Where biology meets cryptography!