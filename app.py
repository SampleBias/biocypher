"""
bi0cyph3r DNA Cryptography System
Copyright (c) 2025 James Utley

Licensed under the bi0cyph3r DNA Cryptography System License.
See LICENSE file for details.

This software is for personal, educational, and research use only.
Commercial use requires explicit written permission.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
import os
import logging
from functools import wraps
import re
from html import escape

from dna_crypto import DNACrypto, DNACryptoError
from nanopore_dna_crypto import NanoporeDNACrypto, NanoporeDNACryptoError
from secure_nanopore_dna_crypto import SecureNanoporeDNACrypto, SecureDNACryptoError
from config import config

# Initialize Flask app
def create_app(config_name=None):
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    csrf = CSRFProtect()
    csrf.init_app(app)
    
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[app.config['RATELIMIT_DEFAULT']]
    )
    limiter.init_app(app)
    
    # Configure logging
    if not app.debug:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(name)s %(message)s'
        )
        app.logger.setLevel(logging.INFO)
    
    return app, limiter, csrf

app, limiter, csrf = create_app()

# Secure user authentication with hashed passwords
USERS = {
    'demo': generate_password_hash('password123')
}

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def validate_and_sanitize_message(message):
    """Validate and sanitize input message"""
    if not message:
        return "", "Please enter a message to encode"
    
    # Remove potential XSS attempts - but preserve newlines
    message = escape(message.rstrip())
    
    # Check length limits
    max_length = app.config.get('MAX_MESSAGE_LENGTH', 1000)
    if len(message) > max_length:
        return "", f"Message too long. Maximum {max_length} characters allowed."
    
    # Check for valid characters (printable ASCII + common whitespace)
    # Allow: printable ASCII (32-126), newline (10), carriage return (13), tab (9)
    valid_chars = set(range(32, 127)) | {9, 10, 13}  # printable + tab, newline, carriage return
    if not all(ord(char) in valid_chars for char in message):
        invalid_chars = [repr(char) for char in message if ord(char) not in valid_chars]
        return "", f"Message contains invalid characters: {', '.join(invalid_chars[:5])}. Only printable ASCII and basic whitespace allowed."
    
    return message, ""

def validate_dna_sequence(sequence):
    """Validate DNA sequence input"""
    if not sequence:
        return "", "Please enter a DNA sequence to decode"
    
    # Remove whitespace and convert to uppercase
    sequence = re.sub(r'\s+', '', sequence.upper())
    
    # Check if sequence contains only valid DNA bases
    if not re.match(r'^[ATCG]+$', sequence):
        return "", "Invalid DNA sequence. Only A, T, C, G are allowed."
    
    # Check length limits
    max_length = app.config.get('MAX_DNA_SEQUENCE_LENGTH', 10000)
    if len(sequence) > max_length:
        return "", f"DNA sequence too long. Maximum {max_length} bases allowed."
    
    return sequence, ""

@app.route('/')
def index():
    """Landing page with login form"""
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in USERS and check_password_hash(USERS[username], password):
            session['user'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Handle user logout"""
    session.pop('user', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard after login"""
    return render_template('dashboard.html', username=session.get('user'))

@app.route('/encode')
@login_required
def encode_page():
    """Page for encoding messages to DNA"""
    return render_template('encode.html')

@app.route('/decode')
@login_required
def decode_page():
    """Page for decoding DNA to messages"""
    return render_template('decode.html')

@app.route('/process_encode', methods=['POST'])
@login_required
@limiter.limit("10 per minute")
def process_encode():
    """Process the encoding form submission"""
    message = request.form.get('message', '')
    mode = request.form.get('mode', 'basic')
    use_error_correction = request.form.get('error_correction') == 'on'
    password = request.form.get('password', '')
    encoded_result = ""
    error = ""
    stats = {}
    security_info = {}
    
    try:
        # Validate and sanitize input
        message, error = validate_and_sanitize_message(message)
        
        if not error:
            if mode == 'secure':
                if not password:
                    error = "Password is required for secure mode"
                else:
                    crypto = SecureNanoporeDNACrypto()
                    # Validate password strength
                    password_validation = crypto.validate_password_strength(password)
                    if not password_validation['valid']:
                        error = f"Password too weak: {', '.join(password_validation['issues'])}"
                    else:
                        encoded_result = crypto.secure_encode_message(message, password, use_error_correction)
                        security_info = crypto.get_security_info()
                        stats = DNACrypto.get_sequence_stats(encoded_result.replace('ATCGATCG', '').replace('CGATATCG', ''))
                        app.logger.info(f"Message encoded (secure mode) successfully by user {session.get('user')}")
            elif mode == 'nanopore':
                encoded_result = NanoporeDNACrypto.encode_message(message, use_error_correction)
                stats = NanoporeDNACrypto.get_nanopore_stats(encoded_result)
                app.logger.info(f"Message encoded (nanopore mode) successfully by user {session.get('user')}")
            else:
                encoded_result = DNACrypto.encode_message(message)
                stats = DNACrypto.get_sequence_stats(encoded_result)
                app.logger.info(f"Message encoded (basic mode) successfully by user {session.get('user')}")
    
    except (DNACryptoError, NanoporeDNACryptoError, SecureDNACryptoError) as e:
        error = str(e)
        app.logger.error(f"Encoding error: {error}")
    except Exception as e:
        error = "An unexpected error occurred during encoding"
        app.logger.error(f"Unexpected encoding error: {str(e)}")
    
    return render_template('encode.html', 
                          message=message,
                          encoded=encoded_result, 
                          error=error,
                          stats=stats,
                          security_info=security_info,
                          mode=mode,
                          use_error_correction=use_error_correction)

@app.route('/process_decode', methods=['POST'])
@login_required
@limiter.limit("10 per minute")
def process_decode():
    """Process the decoding form submission"""
    sequence = request.form.get('sequence', '')
    mode = request.form.get('mode', 'basic')
    use_error_correction = request.form.get('error_correction') == 'on'
    password = request.form.get('password', '')
    decoded_result = ""
    error = ""
    stats = {}
    security_info = {}
    
    try:
        # Validate and sanitize input
        sequence, error = validate_dna_sequence(sequence)
        
        if not error:
            if mode == 'secure':
                if not password:
                    error = "Password is required for secure mode"
                else:
                    crypto = SecureNanoporeDNACrypto()
                    decoded_result = crypto.secure_decode_sequence(sequence, password, use_error_correction)
                    security_info = crypto.get_security_info()
                    stats = DNACrypto.get_sequence_stats(sequence.replace('ATCGATCG', '').replace('CGATATCG', ''))
                    app.logger.info(f"Sequence decoded (secure mode) successfully by user {session.get('user')}")
            elif mode == 'nanopore':
                decoded_result = NanoporeDNACrypto.decode_sequence(sequence, use_error_correction)
                stats = NanoporeDNACrypto.get_nanopore_stats(sequence)
                app.logger.info(f"Sequence decoded (nanopore mode) successfully by user {session.get('user')}")
            else:
                decoded_result = DNACrypto.decode_sequence(sequence)
                stats = DNACrypto.get_sequence_stats(sequence)
                app.logger.info(f"Sequence decoded (basic mode) successfully by user {session.get('user')}")
    
    except (DNACryptoError, NanoporeDNACryptoError, SecureDNACryptoError) as e:
        error = str(e)
        app.logger.error(f"Decoding error: {error}")
    except Exception as e:
        error = "An unexpected error occurred during decoding"
        app.logger.error(f"Unexpected decoding error: {str(e)}")
    
    return render_template('decode.html', 
                          sequence=sequence,
                          decoded=decoded_result, 
                          error=error,
                          stats=stats,
                          security_info=security_info,
                          mode=mode,
                          use_error_correction=use_error_correction)

@app.route('/contact')
def contact():
    """Contact page with email information"""
    return render_template('contact.html')

@app.route('/api/encode', methods=['POST'])
@login_required
def api_encode():
    """API endpoint for encoding"""
    data = request.get_json()
    message = data.get('message', '')
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    encoded = encode_message(message)
    return jsonify({'encoded': encoded})

@app.route('/api/decode', methods=['POST'])
@login_required
def api_decode():
    """API endpoint for decoding"""
    data = request.get_json()
    sequence = data.get('sequence', '')
    if not sequence:
        return jsonify({'error': 'No DNA sequence provided'}), 400
    
    # Validate sequence
    if not all(base in 'ATCG' for base in sequence):
        return jsonify({'error': 'Invalid DNA sequence. Only A, T, C, G are allowed.'}), 400
    
    decoded = decode_sequence(sequence)
    return jsonify({'decoded': decoded})

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Server Error: {error}')
    return render_template('error.html', 
                         error_code=500, 
                         error_message="Internal server error"), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template('error.html', 
                         error_code=429, 
                         error_message="Rate limit exceeded. Please try again later."), 429

if __name__ == '__main__':
    app.run(debug=True) 