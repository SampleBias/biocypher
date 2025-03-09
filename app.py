from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management and flash messages

# DNA base mapping for binary values
DNA_ENCODE = {
    '00': 'A',
    '01': 'T',
    '10': 'C',
    '11': 'G'
}

# Reverse mapping for decoding
DNA_DECODE = {v: k for k, v in DNA_ENCODE.items()}

# Simple user authentication (in a real app, use a database and proper password hashing)
USERS = {
    'demo': 'password123'
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

def text_to_binary(text):
    """Convert text to binary representation"""
    binary = ''
    for char in text:
        # Convert character to ASCII, then to 8-bit binary
        ascii_val = ord(char)
        bin_val = format(ascii_val, '08b')
        binary += bin_val
    return binary

def binary_to_dna(binary):
    """Convert binary to DNA sequence"""
    dna = ''
    # Process binary string in pairs
    for i in range(0, len(binary), 2):
        if i + 1 < len(binary):
            pair = binary[i:i+2]
            dna += DNA_ENCODE[pair]
        else:
            # Handle odd-length binary by padding
            pair = binary[i] + '0'
            dna += DNA_ENCODE[pair]
    return dna

def dna_to_binary(dna):
    """Convert DNA sequence to binary"""
    binary = ''
    for base in dna:
        if base in DNA_DECODE:
            binary += DNA_DECODE[base]
        else:
            # Skip invalid bases
            continue
    return binary

def binary_to_text(binary):
    """Convert binary to text"""
    text = ''
    # Process binary in 8-bit chunks
    for i in range(0, len(binary), 8):
        if i + 8 <= len(binary):
            byte = binary[i:i+8]
            ascii_val = int(byte, 2)
            text += chr(ascii_val)
    return text

def encode_message(message):
    """Encode a message into DNA sequence"""
    if not message:
        return ""
    binary = text_to_binary(message)
    dna = binary_to_dna(binary)
    return dna

def decode_sequence(sequence):
    """Decode a DNA sequence back to the original message"""
    if not sequence:
        return ""
    # Validate input - only A, T, C, G allowed
    valid_bases = set('ATCG')
    if not all(base in valid_bases for base in sequence):
        return "Error: Invalid DNA sequence. Only A, T, C, G are allowed."
    
    binary = dna_to_binary(sequence)
    text = binary_to_text(binary)
    return text

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
        
        if username in USERS and USERS[username] == password:
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
def process_encode():
    """Process the encoding form submission"""
    message = request.form.get('message', '')
    encoded_result = ""
    error = ""
    
    if message:
        encoded_result = encode_message(message)
    else:
        error = "Please enter a message to encode"
    
    return render_template('encode.html', 
                          message=message,
                          encoded=encoded_result, 
                          error=error)

@app.route('/process_decode', methods=['POST'])
@login_required
def process_decode():
    """Process the decoding form submission"""
    sequence = request.form.get('sequence', '')
    decoded_result = ""
    error = ""
    
    if sequence:
        # Check if sequence contains only valid DNA bases
        if not all(base in 'ATCG' for base in sequence):
            error = "Invalid DNA sequence. Only A, T, C, G are allowed."
        else:
            decoded_result = decode_sequence(sequence)
    else:
        error = "Please enter a DNA sequence to decode"
    
    return render_template('decode.html', 
                          sequence=sequence,
                          decoded=decoded_result, 
                          error=error)

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

if __name__ == '__main__':
    app.run(debug=True) 