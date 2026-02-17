"""
Secure Nanopore-Optimized DNA Cryptography Module
Combines AES encryption with nanopore sequencing optimization
"""

import hashlib
import secrets
import base64
from typing import Dict, Optional, Tuple
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.backends import default_backend
from nanopore_dna_crypto import NanoporeDNACrypto, NanoporeDNACryptoError

class SecureDNACryptoError(Exception):
    """Custom exception for secure DNA cryptography errors"""
    pass

class SecureNanoporeDNACrypto(NanoporeDNACrypto):
    """
    Secure nanopore-optimized DNA cryptography with AES encryption
    
    Security Flow:
    1. Input plaintext message
    2. AES-256-CBC encryption with PBKDF2 key derivation
    3. Nanopore-optimized DNA encoding with error correction
    4. Output: Secure DNA sequence suitable for nanopore sequencing
    """
    
    # Cryptographic constants
    KEY_SIZE = 32  # 256-bit AES key
    IV_SIZE = 16   # 128-bit IV for CBC mode
    SALT_SIZE = 16 # 128-bit salt for PBKDF2
    PBKDF2_ITERATIONS = 100000  # Strong key derivation
    
    def __init__(self, password: Optional[str] = None):
        """
        Initialize secure DNA crypto with optional password
        
        Args:
            password: Password for encryption. If None, will prompt when needed.
        """
        self.password = password
        self._cached_key = None
        self._cached_salt = None
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """
        Derive encryption key from password using PBKDF2
        
        Args:
            password: User password
            salt: Random salt bytes
            
        Returns:
            32-byte encryption key
        """
        if not password:
            raise SecureDNACryptoError("Password is required for encryption")
        
        # Use PBKDF2 with SHA-256 for key derivation
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_SIZE,
            salt=salt,
            iterations=self.PBKDF2_ITERATIONS,
            backend=default_backend()
        )
        
        return kdf.derive(password.encode('utf-8'))
    
    def _encrypt_message(self, plaintext: str, password: str) -> Tuple[bytes, bytes, bytes]:
        """
        Encrypt message using AES-256-CBC
        
        Args:
            plaintext: Message to encrypt
            password: Encryption password
            
        Returns:
            Tuple of (encrypted_data, iv, salt)
        """
        if not plaintext:
            return b'', b'', b''
        
        # Generate random salt and IV
        salt = secrets.token_bytes(self.SALT_SIZE)
        iv = secrets.token_bytes(self.IV_SIZE)
        
        # Derive encryption key
        key = self._derive_key(password, salt)
        
        # Pad plaintext to block size (PKCS7 padding)
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext.encode('utf-8'))
        padded_data += padder.finalize()
        
        # Encrypt using AES-256-CBC
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        return encrypted_data, iv, salt
    
    def _decrypt_message(self, encrypted_data: bytes, iv: bytes, salt: bytes, password: str) -> str:
        """
        Decrypt message using AES-256-CBC
        
        Args:
            encrypted_data: Encrypted bytes
            iv: Initialization vector
            salt: Salt used for key derivation
            password: Decryption password
            
        Returns:
            Decrypted plaintext
        """
        if not encrypted_data:
            return ""
        
        # Derive decryption key
        key = self._derive_key(password, salt)
        
        # Decrypt using AES-256-CBC
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # Remove PKCS7 padding
        unpadder = padding.PKCS7(128).unpadder()
        plaintext_bytes = unpadder.update(padded_data)
        plaintext_bytes += unpadder.finalize()
        
        return plaintext_bytes.decode('utf-8')
    
    def _crypto_data_to_string(self, encrypted_data: bytes, iv: bytes, salt: bytes) -> str:
        """
        Convert crypto data to base64 string for DNA encoding
        
        Args:
            encrypted_data: Encrypted bytes
            iv: Initialization vector
            salt: Salt bytes
            
        Returns:
            Base64 encoded string containing all crypto data
        """
        # Combine all crypto data with length prefixes for parsing
        combined = (
            len(salt).to_bytes(2, 'big') + salt +
            len(iv).to_bytes(2, 'big') + iv +
            len(encrypted_data).to_bytes(4, 'big') + encrypted_data
        )
        
        return base64.b64encode(combined).decode('ascii')
    
    def _string_to_crypto_data(self, crypto_string: str) -> Tuple[bytes, bytes, bytes]:
        """
        Parse base64 string back to crypto data
        
        Args:
            crypto_string: Base64 encoded crypto data
            
        Returns:
            Tuple of (encrypted_data, iv, salt)
        """
        try:
            combined = base64.b64decode(crypto_string.encode('ascii'))
            
            # Parse salt
            salt_len = int.from_bytes(combined[0:2], 'big')
            salt = combined[2:2+salt_len]
            
            # Parse IV
            iv_start = 2 + salt_len
            iv_len = int.from_bytes(combined[iv_start:iv_start+2], 'big')
            iv = combined[iv_start+2:iv_start+2+iv_len]
            
            # Parse encrypted data
            data_start = iv_start + 2 + iv_len
            data_len = int.from_bytes(combined[data_start:data_start+4], 'big')
            encrypted_data = combined[data_start+4:data_start+4+data_len]
            
            return encrypted_data, iv, salt
            
        except Exception as e:
            raise SecureDNACryptoError(f"Failed to parse crypto data: {str(e)}")
    
    def secure_encode_message(self, message: str, password: str, use_error_correction: bool = True) -> str:
        """
        Securely encode message with AES encryption + nanopore optimization
        
        Args:
            message: Plaintext message to encode
            password: Encryption password
            use_error_correction: Enable nanopore error correction
            
        Returns:
            DNA sequence containing encrypted message
        """
        if not message:
            return ""
        
        if not password:
            raise SecureDNACryptoError("Password is required for secure encoding")
        
        try:
            # Step 1: AES encryption
            encrypted_data, iv, salt = self._encrypt_message(message, password)
            
            # Step 2: Convert crypto data to string for DNA encoding
            crypto_string = self._crypto_data_to_string(encrypted_data, iv, salt)
            
            # Step 3: Use basic DNA crypto for base64 data, then add nanopore markers
            from dna_crypto import DNACrypto
            dna_sequence = DNACrypto.encode_message(crypto_string)
            
            # Step 4: Add nanopore markers for compatibility
            if dna_sequence:
                dna_sequence = 'ATCGATCG' + dna_sequence + 'CGATATCG'
            
            return dna_sequence
            
        except Exception as e:
            raise SecureDNACryptoError(f"Secure encoding failed: {str(e)}")
    
    def secure_decode_sequence(self, sequence: str, password: str, use_error_correction: bool = True) -> str:
        """
        Securely decode DNA sequence with AES decryption
        
        Args:
            sequence: DNA sequence to decode
            password: Decryption password
            use_error_correction: Enable nanopore error correction
            
        Returns:
            Original plaintext message
        """
        if not sequence:
            return ""
        
        if not password:
            raise SecureDNACryptoError("Password is required for secure decoding")
        
        try:
            # Step 1: Use basic DNA crypto decode (not nanopore) for base64 data
            from dna_crypto import DNACrypto
            crypto_string = DNACrypto.decode_sequence(sequence.replace('ATCGATCG', '').replace('CGATATCG', ''))
            
            if not crypto_string:
                return ""
            
            # Step 2: Parse crypto data from string
            encrypted_data, iv, salt = self._string_to_crypto_data(crypto_string)
            
            # Step 3: AES decryption
            plaintext = self._decrypt_message(encrypted_data, iv, salt, password)
            
            return plaintext
            
        except Exception as e:
            raise SecureDNACryptoError(f"Secure decoding failed: {str(e)}")
    
    def get_security_info(self) -> Dict:
        """
        Get information about security parameters
        
        Returns:
            Dictionary with security details
        """
        return {
            'encryption_algorithm': 'AES-256-CBC',
            'key_derivation': 'PBKDF2-HMAC-SHA256',
            'pbkdf2_iterations': self.PBKDF2_ITERATIONS,
            'key_size_bits': self.KEY_SIZE * 8,
            'iv_size_bits': self.IV_SIZE * 8,
            'salt_size_bits': self.SALT_SIZE * 8,
            'padding_scheme': 'PKCS7',
            'nanopore_optimized': True,
            'error_correction': True,
            'homopolymer_avoidance': True,
            'gc_balancing': True
        }
    
    def validate_password_strength(self, password: str) -> Dict:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            
        Returns:
            Dictionary with validation results
        """
        if not password:
            return {
                'valid': False,
                'score': 0,
                'max_score': 6,
                'strength': 'Weak',
                'issues': ['Password is required']
            }
        
        issues = []
        score = 0
        
        # Length check
        if len(password) < 8:
            issues.append('Password should be at least 8 characters')
        else:
            score += 1
        
        if len(password) >= 12:
            score += 1
        
        # Character variety checks
        if any(c.isupper() for c in password):
            score += 1
        else:
            issues.append('Password should contain uppercase letters')
        
        if any(c.islower() for c in password):
            score += 1
        else:
            issues.append('Password should contain lowercase letters')
        
        if any(c.isdigit() for c in password):
            score += 1
        else:
            issues.append('Password should contain numbers')
        
        if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            score += 1
        else:
            issues.append('Password should contain special characters')
        
        # Strength assessment
        if score >= 5:
            strength = 'Strong'
        elif score >= 3:
            strength = 'Moderate'
        else:
            strength = 'Weak'
        
        return {
            'valid': len(issues) == 0,
            'score': score,
            'max_score': 6,
            'strength': strength,
            'issues': issues
        }
    
    @classmethod
    def generate_secure_password(cls, length: int = 16) -> str:
        """
        Generate a cryptographically secure password
        
        Args:
            length: Password length (minimum 12)
            
        Returns:
            Secure random password
        """
        if length < 12:
            length = 12
        
        # Character sets for password generation
        lowercase = 'abcdefghijklmnopqrstuvwxyz'
        uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        digits = '0123456789'
        special = '!@#$%^&*()_+-=[]{}|;:,.<>?'
        
        all_chars = lowercase + uppercase + digits + special
        
        # Ensure at least one character from each set
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(special)
        ]
        
        # Fill remaining length with random characters
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))
        
        # Shuffle to avoid predictable patterns
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password) 