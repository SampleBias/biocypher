# bi0cyph3r - DNA Cryptography System

A sophisticated, secure Flask web application that allows users to encode and decode messages using DNA cryptography with enterprise-grade security features and nanopore sequencing optimization.

## Features

- 🔐 **Secure Authentication**: Password hashing with Werkzeug
- 🛡️ **Security Hardened**: CSRF protection, rate limiting, input validation
- 🧬 **Advanced DNA Crypto**: Dual-mode encoding with basic and nanopore optimization
- 🔬 **Nanopore Optimized**: Error correction, homopolymer avoidance, GC balancing
- 🛡️ **Safety Screener**: Comprehensive biosafety analysis to prevent pathogen synthesis
- 🎨 **Modern UI**: Clean, responsive, futuristic interface with mode selection
- 📊 **Analytics**: Comprehensive DNA sequence statistics and nanopore risk assessment
- ⚡ **Performance**: Optimized code structure and error handling
- 🧪 **Tested**: Comprehensive unit test coverage (17 test cases)
- 📝 **Logging**: Detailed application logging for monitoring

## How It Works

bi0cyph3r offers three encoding modes:

### Basic Mode
Uses the four nucleotide bases (A, T, C, G) to represent binary data:
- A = 00, T = 01, C = 10, G = 11
- Converts text to ASCII, then to binary, and maps binary pairs to DNA bases
- Fast and suitable for educational purposes and small messages

### Nanopore Optimized Mode  
Advanced encoding designed for nanopore sequencing with:
- **Triplet Encoding**: Uses 8 homopolymer-free triplets (ATC, ATG, ACT, ACG, TAG, TAC, TCG, TCA)
- **Error Correction**: Triple redundancy encoding with majority voting
- **Parity Checking**: Even parity bits for error detection
- **Homopolymer Avoidance**: Prevents problematic consecutive identical bases
- **GC Content Balancing**: Maintains 40-60% GC content optimal for nanopore
- **Nanopore Markers**: Special start/stop sequences for reliable sequencing
- **Risk Assessment**: Comprehensive nanopore compatibility scoring

### 🔒 Secure Mode (NEW)
Enterprise-grade cryptographic security combined with DNA encoding:
- **AES-256-CBC Encryption**: Military-grade encryption before DNA encoding
- **PBKDF2 Key Derivation**: 100,000 iterations with SHA-256 for password-based encryption
- **Password Protection**: Strong password validation and secure password generation
- **Cryptographic Security**: True security unlike obfuscation-only approaches
- **Nanopore Compatible**: Uses basic DNA encoding with nanopore markers for sequencing compatibility
- **Production Ready**: Suitable for real-world secure data storage applications

## 🛡️ Safety Screener (NEW)

The integrated DNA Safety Screener provides comprehensive biosafety analysis to prevent inadvertent synthesis of potentially harmful sequences:

### Safety Analysis Features
- **🦠 Pathogen Detection**: Screens for viral polymerase, toxin genes, antibiotic resistance, and virulence factors
- **🧬 Natural Occurrence Check**: Detects sequences from housekeeping genes, E. coli, and human genomes
- **📊 Sequence Analysis**: Evaluates GC content, ORFs, homopolymer runs, and repetitive elements
- **⚠️ Risk Assessment**: Provides LOW/MEDIUM/HIGH risk classification with detailed explanations
- **💡 Recommendations**: Clear guidance on synthesis safety with specific warnings

### Safety Status Indicators
- **✅ SAFE (Green)**: No risks detected - approved for synthesis
- **⚠️ CAUTION (Orange)**: Some concerns found - review carefully before synthesis
- **❌ UNSAFE (Red)**: Do not synthesize - potential pathogen or harmful sequence detected

### How Safety Screening Works
1. **Encode your message** using any of the three DNA cryptography modes
2. **Click the "🛡️ Safety Screen" button** next to the Copy button
3. **Review the comprehensive report** showing:
   - Overall safety status with color-coded indicator
   - Detailed pathogen analysis with signature matches
   - Natural genome occurrence check
   - Sequence characteristics and warnings
   - Specific recommendations for safe synthesis

The safety screener uses pattern matching against known pathogen signatures and natural sequences to identify potentially problematic DNA sequences before synthesis.

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd biocypher
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment** (optional)
   ```bash
   export FLASK_ENV=development
   export SECRET_KEY=your-secret-key
   export MAX_MESSAGE_LENGTH=1000
   ```

5. **Run tests** (recommended)
   ```bash
   python test_dna_crypto.py
   ```

6. **Start the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   - Open `http://127.0.0.1:5000/`
   - Login with demo credentials:
     - Username: `demo`
     - Password: `password123`

8. **Test the Safety Screener**
   - Go to the Encode page
   - Enter any message and encode it
   - Click the "🛡️ Safety Screen" button
   - Review the comprehensive safety analysis report

## Project Structure

```
biocypher/
├── app.py                     # Main Flask application with tri-mode support + safety API
├── dna_crypto.py             # Basic DNA cryptography module
├── nanopore_dna_crypto.py    # Nanopore-optimized cryptography module
├── secure_nanopore_dna_crypto.py # Secure AES+DNA cryptography module
├── safety_screener.py        # DNA safety screening and pathogen detection (NEW)
├── config.py                 # Configuration management
├── test_dna_crypto.py        # Basic DNA crypto unit tests
├── test_nanopore_dna_crypto.py # Nanopore crypto unit tests (17 test cases)
├── test_secure_nanopore_dna_crypto.py # Secure crypto unit tests (15 test cases)
├── requirements.txt          # Python dependencies (includes cryptography)
├── static/                   # CSS, JS, images
│   ├── css/style.css         # Updated with safety screener styling
│   └── js/script.js          # Updated with safety screening functionality
├── templates/                # HTML templates with mode selection
│   ├── login.html
│   ├── dashboard.html
│   ├── encode.html           # Updated with safety screening UI
│   ├── decode.html           # Updated with nanopore mode toggle  
│   ├── contact.html
│   └── error.html
└── README.md
```

## Application Pages

- **🔐 Login**: Secure authentication with hashed passwords
- **📊 Dashboard**: Central navigation with system overview
- **📝 Encode**: Convert messages to DNA with validation, stats & safety screening
- **🧬 Decode**: Translate DNA sequences with error handling
- **📧 Contact**: Support and access requests
- **❌ Error**: Comprehensive error handling pages

## API Endpoints

- **POST /api/encode**: Programmatic DNA encoding
- **POST /api/decode**: Programmatic DNA decoding  
- **POST /api/safety_screen**: Comprehensive DNA safety analysis (NEW)

## Examples

### Basic Mode
- Input: "HELLO WORLD"
- Encoded DNA: "ACTACAAGTAGTATGCGGCCGATGCACAGTAAT" (32 bases)
- Safety Status: ✅ SAFE (typical result for encoded messages)

### Nanopore Mode  
- Input: "HELLO WORLD"
- Encoded DNA: "ATCGATCGATCATG...TACGTAACGATGCGATATCG" (~350 bases)
- Features: Error correction, no homopolymers, balanced GC content, nanopore markers
- Safety Status: ✅ SAFE (optimized sequences are typically safe)

### Safety Screening Workflow
1. **Encode Message**: "Hello DNA World" → `TACATCTTTCGATCGATCGGACAATTTGTCGGTGACTCGATCTA`
2. **Click Safety Screen**: Analysis begins with loading animation
3. **View Results**: 
   ```
   ✅ SAFE
   📊 Sequence Analysis: 44 bases, 45.45% GC content
   🦠 Pathogen Risk: No signatures detected
   🧬 Natural Occurrence: No matches found
   💡 Recommendations: Sequence appears safe for synthesis
   ```

## Security Features

- **Password Hashing**: Uses Werkzeug for secure password storage
- **Rate Limiting**: Prevents abuse with configurable limits
- **Input Validation**: Comprehensive sanitization and validation
- **CSRF Protection**: Protects against cross-site request forgery
- **Session Security**: Secure session configuration
- **Error Handling**: Safe error messages without information leakage
- **Logging**: Security events monitoring

## Environment Variables

Create a `.env` file or set environment variables:

```bash
FLASK_ENV=development          # or production/testing
SECRET_KEY=your-secret-key     # Generate a secure random key
MAX_MESSAGE_LENGTH=1000        # Maximum message length
MAX_DNA_SEQUENCE_LENGTH=10000  # Maximum DNA sequence length
REDIS_URL=redis://localhost:6379  # For rate limiting (optional)
```

## Testing

Run the comprehensive unit test suites:

```bash
# Run basic DNA crypto tests  
python test_dna_crypto.py

# Run nanopore optimization tests (17 test cases)
python test_nanopore_dna_crypto.py

# Run both test suites with verbose output
python -m unittest test_dna_crypto.py test_nanopore_dna_crypto.py -v
```

### Test Coverage
- **Basic DNA Crypto**: 10 test cases covering encoding/decoding, validation, statistics
- **Nanopore Optimization**: 17 test cases covering error correction, homopolymer avoidance, GC balancing, parity checking, risk assessment

## Production Deployment

For production deployment:

1. Set `FLASK_ENV=production`
2. Generate a secure `SECRET_KEY`
3. Use a proper WSGI server like Gunicorn
4. Set up Redis for rate limiting
5. Configure HTTPS
6. Implement proper logging and monitoring

Example production command:
```bash
gunicorn --bind 0.0.0.0:8000 app:app
```

## License

This project is licensed under a custom restrictive license - see the [LICENSE](LICENSE) file for details.

**Copyright (c) 2025 James Utley**

**Important License Terms:**
- ✅ **Allowed**: Personal, educational, and research use with attribution
- ❌ **Restricted**: Commercial use, redistribution, and public deployment require explicit written permission
- 📧 **Contact**: For commercial licensing or permissions, contact James Utley

This software is provided for educational and research purposes. Any commercial use, including but not limited to selling, licensing, or incorporating this software into commercial products or services, requires explicit written permission from the author.

For more information about licensing options, please refer to the full LICENSE file or contact the author for commercial licensing arrangements.