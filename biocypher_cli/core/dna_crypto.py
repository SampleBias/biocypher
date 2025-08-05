"""
DNA Cryptography Module
Handles encoding and decoding of messages using DNA bases
"""

class DNACryptoError(Exception):
    """Custom exception for DNA cryptography errors"""
    pass

class DNACrypto:
    """DNA Cryptography class with encoding/decoding functionality"""
    
    # DNA base mapping for binary values
    DNA_ENCODE = {
        '00': 'A',
        '01': 'T',
        '10': 'C',
        '11': 'G'
    }
    
    # Reverse mapping for decoding
    DNA_DECODE = {v: k for k, v in DNA_ENCODE.items()}
    
    @staticmethod
    def text_to_binary(text):
        """Convert text to binary representation"""
        if not text:
            return ""
        
        binary = ''
        for char in text:
            # Convert character to ASCII, then to 8-bit binary
            ascii_val = ord(char)
            bin_val = format(ascii_val, '08b')
            binary += bin_val
        return binary
    
    @staticmethod
    def binary_to_dna(binary):
        """Convert binary to DNA sequence"""
        if not binary:
            return ""
        
        dna = ''
        # Process binary string in pairs
        for i in range(0, len(binary), 2):
            if i + 1 < len(binary):
                pair = binary[i:i+2]
                dna += DNACrypto.DNA_ENCODE[pair]
            else:
                # Handle odd-length binary by padding
                pair = binary[i] + '0'
                dna += DNACrypto.DNA_ENCODE[pair]
        return dna
    
    @staticmethod
    def dna_to_binary(dna):
        """Convert DNA sequence to binary"""
        if not dna:
            return ""
        
        binary = ''
        for base in dna:
            if base in DNACrypto.DNA_DECODE:
                binary += DNACrypto.DNA_DECODE[base]
            else:
                # Skip invalid bases
                continue
        return binary
    
    @staticmethod
    def binary_to_text(binary):
        """Convert binary to text"""
        if not binary:
            return ""
        
        text = ''
        # Process binary in 8-bit chunks
        for i in range(0, len(binary), 8):
            if i + 8 <= len(binary):
                byte = binary[i:i+8]
                try:
                    ascii_val = int(byte, 2)
                    if 32 <= ascii_val <= 126:  # Printable ASCII range
                        text += chr(ascii_val)
                except ValueError:
                    continue
        return text
    
    @classmethod
    def encode_message(cls, message):
        """Encode a message into DNA sequence"""
        if not message:
            return ""
        
        try:
            binary = cls.text_to_binary(message)
            dna = cls.binary_to_dna(binary)
            return dna
        except Exception as e:
            raise DNACryptoError(f"Encoding failed: {str(e)}")
    
    @classmethod
    def decode_sequence(cls, sequence):
        """Decode a DNA sequence back to the original message"""
        if not sequence:
            return ""
        
        try:
            binary = cls.dna_to_binary(sequence)
            text = cls.binary_to_text(binary)
            return text
        except Exception as e:
            raise DNACryptoError(f"Decoding failed: {str(e)}")
    
    @staticmethod
    def get_sequence_stats(sequence):
        """Get statistics about a DNA sequence"""
        if not sequence:
            return {}
        
        stats = {
            'length': len(sequence),
            'bases': {
                'A': sequence.count('A'),
                'T': sequence.count('T'),
                'C': sequence.count('C'),
                'G': sequence.count('G')
            },
            'gc_content': round((sequence.count('G') + sequence.count('C')) / len(sequence) * 100, 2)
        }
        return stats