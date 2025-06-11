# bi0cyph3r - DNA Cryptography System

A sophisticated, secure Flask web application that allows users to encode and decode messages using DNA cryptography with enterprise-grade security features.

## Features

- 🔐 **Secure Authentication**: Password hashing with Werkzeug
- 🛡️ **Security Hardened**: CSRF protection, rate limiting, input validation
- 🧬 **Advanced DNA Crypto**: Modular cryptography system with error handling
- 🎨 **Modern UI**: Clean, responsive, futuristic interface
- 📊 **Analytics**: DNA sequence statistics and insights
- ⚡ **Performance**: Optimized code structure and error handling
- 🧪 **Tested**: Comprehensive unit test coverage
- 📝 **Logging**: Detailed application logging for monitoring

## How It Works

bi0cyph3r uses the four nucleotide bases (A, T, C, G) to represent binary data:
- A = 00
- T = 01
- C = 10
- G = 11

The application converts text to ASCII, then to binary, and finally maps the binary values to DNA bases.

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

## Project Structure

```
biocypher/
├── app.py                 # Main Flask application
├── dna_crypto.py         # DNA cryptography module
├── config.py             # Configuration management
├── test_dna_crypto.py    # Unit tests
├── requirements.txt      # Python dependencies
├── static/               # CSS, JS, images
├── templates/            # HTML templates
│   ├── login.html
│   ├── dashboard.html
│   ├── encode.html
│   ├── decode.html
│   ├── contact.html
│   └── error.html
└── README.md
```

## Application Pages

- **🔐 Login**: Secure authentication with hashed passwords
- **📊 Dashboard**: Central navigation with system overview
- **📝 Encode**: Convert messages to DNA with validation & stats
- **🧬 Decode**: Translate DNA sequences with error handling
- **📧 Contact**: Support and access requests
- **❌ Error**: Comprehensive error handling pages

## Example

- Input: "HELLO WORLD"
- Encoded DNA Sequence: "ACTACAAGTAGTATGCGGCCGATGCACAGTAAT"

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

Run the unit tests to verify functionality:

```bash
# Run DNA crypto tests  
python test_dna_crypto.py

# Run all tests with verbose output
python -m unittest test_dna_crypto.py -v
```

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