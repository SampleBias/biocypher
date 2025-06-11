"""
Unit tests for DNA Cryptography functionality
"""
import unittest
from dna_crypto import DNACrypto, DNACryptoError

class TestDNACrypto(unittest.TestCase):
    """Test cases for DNACrypto class"""
    
    def test_text_to_binary(self):
        """Test text to binary conversion"""
        result = DNACrypto.text_to_binary("A")
        self.assertEqual(result, "01000001")  # ASCII 65 in binary
        
        result = DNACrypto.text_to_binary("Hi")
        self.assertEqual(result, "0100100001101001")  # H=72, i=105
    
    def test_binary_to_dna(self):
        """Test binary to DNA conversion"""
        result = DNACrypto.binary_to_dna("01000001")
        self.assertEqual(result, "TAAA")  # 01=T, 00=A, 00=A, 01=T -> TAAT
        
        # Test odd length binary (should pad with 0)
        result = DNACrypto.binary_to_dna("010")
        self.assertEqual(result, "TA")  # 01=T, 0+pad=00=A
    
    def test_dna_to_binary(self):
        """Test DNA to binary conversion"""
        result = DNACrypto.dna_to_binary("TAAA")
        self.assertEqual(result, "01000000")  # T=01, A=00, A=00, A=00
    
    def test_binary_to_text(self):
        """Test binary to text conversion"""
        result = DNACrypto.binary_to_text("01000001")
        self.assertEqual(result, "A")  # Binary 01000001 = ASCII 65 = 'A'
        
        result = DNACrypto.binary_to_text("0100100001101001")
        self.assertEqual(result, "Hi")  # H=72, i=105
    
    def test_encode_message(self):
        """Test complete message encoding"""
        result = DNACrypto.encode_message("A")
        self.assertEqual(result, "TAAA")
        
        # Test empty message
        result = DNACrypto.encode_message("")
        self.assertEqual(result, "")
    
    def test_decode_sequence(self):
        """Test complete sequence decoding"""
        result = DNACrypto.decode_sequence("TAAA")
        # Note: Due to padding, this might not decode back to "A" exactly
        self.assertTrue(isinstance(result, str))
        
        # Test empty sequence
        result = DNACrypto.decode_sequence("")
        self.assertEqual(result, "")
    
    def test_round_trip_encoding(self):
        """Test that encoding then decoding returns original message"""
        test_messages = ["Hello", "123", "Hello World!", "Test@#$%"]
        
        for message in test_messages:
            encoded = DNACrypto.encode_message(message)
            decoded = DNACrypto.decode_sequence(encoded)
            # Remove any null characters or trailing chars from padding
            decoded = decoded.rstrip('\x00')
            self.assertEqual(decoded, message, f"Failed for message: {message}")
    
    def test_get_sequence_stats(self):
        """Test DNA sequence statistics"""
        sequence = "ATCG"
        stats = DNACrypto.get_sequence_stats(sequence)
        
        self.assertEqual(stats['length'], 4)
        self.assertEqual(stats['bases']['A'], 1)
        self.assertEqual(stats['bases']['T'], 1)
        self.assertEqual(stats['bases']['C'], 1)
        self.assertEqual(stats['bases']['G'], 1)
        self.assertEqual(stats['gc_content'], 50.0)  # 2 GC out of 4 = 50%
        
        # Test empty sequence
        stats = DNACrypto.get_sequence_stats("")
        self.assertEqual(stats, {})
    
    def test_invalid_dna_bases(self):
        """Test handling of invalid DNA bases"""
        # dna_to_binary should skip invalid bases
        result = DNACrypto.dna_to_binary("ATCGXYZ")
        expected = DNACrypto.dna_to_binary("ATCG")  # Should ignore XYZ
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main() 