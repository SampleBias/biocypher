"""
Utility functions for BioCypher CLI
"""

import os
import sys
import re
from pathlib import Path
from typing import Optional, Dict, Any, Union
import json
from .formatters import console, OutputFormatter

# Try to import yaml, provide fallback if not available
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

def detect_input_type(input_text: str) -> str:
    """
    Detect if input is a DNA sequence or regular text
    
    Args:
        input_text: Input string to analyze
        
    Returns:
        'dna' if DNA sequence, 'text' if regular text
    """
    # Remove whitespace
    cleaned = re.sub(r'\s+', '', input_text.upper())
    
    # Check if it's primarily DNA bases
    if len(cleaned) > 0:
        dna_bases = sum(1 for c in cleaned if c in 'ATCG')
        ratio = dna_bases / len(cleaned)
        
        # If >80% are valid DNA bases, consider it DNA
        if ratio > 0.8:
            return 'dna'
    
    return 'text'

def detect_encoding_mode(dna_sequence: str) -> str:
    """
    Detect which encoding mode was likely used for a DNA sequence
    
    Args:
        dna_sequence: DNA sequence to analyze
        
    Returns:
        'basic', 'nanopore', or 'secure'
    """
    # Check for nanopore markers
    if 'ATCGATCG' in dna_sequence and 'CGATATCG' in dna_sequence:
        # Could be nanopore or secure mode
        # Check for secure mode patterns (more regular structure)
        inner_sequence = dna_sequence.replace('ATCGATCG', '').replace('CGATATCG', '')
        
        # If it looks very regular (base64-like after DNA encoding), it's likely secure
        if len(inner_sequence) % 4 == 0:
            return 'secure'
        else:
            return 'nanopore'
    
    # Default to basic mode
    return 'basic'

def read_file_content(file_path: Union[str, Path]) -> str:
    """
    Read content from a file, handling various formats
    
    Args:
        file_path: Path to file
        
    Returns:
        File content as string
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        # Try to read as text
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # Handle FASTA format
        if content.startswith('>'):
            lines = content.split('\n')
            # Skip header lines and join sequence lines
            sequence_lines = [line for line in lines if not line.startswith('>')]
            content = ''.join(sequence_lines)
        
        return content
        
    except UnicodeDecodeError:
        raise ValueError(f"File {file_path} is not a valid text file")

def write_file_content(file_path: Union[str, Path], content: str, format_type: str = 'text') -> None:
    """
    Write content to a file with optional formatting
    
    Args:
        file_path: Path to output file
        content: Content to write
        format_type: 'text', 'fasta', 'json'
    """
    file_path = Path(file_path)
    
    # Create directory if it doesn't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    if format_type == 'fasta':
        # Write in FASTA format
        timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
        header = f">BioCypher_sequence_{timestamp}\n"
        formatted_content = header + content
    elif format_type == 'json':
        # Write as JSON
        data = {
            'sequence': content,
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'tool': 'BioCypher CLI'
        }
        formatted_content = json.dumps(data, indent=2)
    else:
        # Plain text
        formatted_content = content
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(formatted_content)

def validate_dna_sequence(sequence: str) -> tuple[bool, str]:
    """
    Validate a DNA sequence
    
    Args:
        sequence: DNA sequence to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not sequence:
        return False, "Empty sequence"
    
    # Remove whitespace
    cleaned = re.sub(r'\s+', '', sequence.upper())
    
    # Check for valid characters
    if not re.match(r'^[ATCG]+$', cleaned):
        invalid_chars = set(c for c in cleaned if c not in 'ATCG')
        return False, f"Invalid characters found: {', '.join(sorted(invalid_chars))}"
    
    # Check minimum length
    if len(cleaned) < 4:
        return False, "Sequence too short (minimum 4 bases)"
    
    return True, ""

def load_config(config_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """
    Load configuration from file
    
    Args:
        config_path: Path to config file, or None for default locations
        
    Returns:
        Configuration dictionary
    """
    # Default configuration
    default_config = {
        'max_message_length': 1000,
        'max_dna_sequence_length': 10000,
        'default_encoding_mode': 'basic',
        'output_format': 'text',
        'colors_enabled': True,
        'progress_bars': True
    }
    
    if config_path is None:
        # Check default locations
        possible_paths = [
            Path.home() / '.biocypher.yaml',
            Path.home() / '.biocypher.yml',
            Path.cwd() / 'biocypher.yaml',
            Path.cwd() / 'biocypher.yml'
        ]
        
        for path in possible_paths:
            if path.exists():
                config_path = path
                break
    
    if config_path and Path(config_path).exists():
        try:
            if not HAS_YAML:
                console.print("⚠️ PyYAML not installed. Configuration file support disabled.")
                return default_config
                
            with open(config_path, 'r') as f:
                file_config = yaml.safe_load(f) or {}
            
            # Merge with defaults
            default_config.update(file_config)
            console.print(f"✅ Loaded configuration from {config_path}")
            
        except Exception as e:
            console.print(f"⚠️ Failed to load config from {config_path}: {e}")
    
    return default_config

def save_config(config: Dict[str, Any], config_path: Optional[Union[str, Path]] = None) -> None:
    """
    Save configuration to file
    
    Args:
        config: Configuration dictionary
        config_path: Path to save config, or None for default location
    """
    if config_path is None:
        config_path = Path.home() / '.biocypher.yaml'
    
    config_path = Path(config_path)
    
    try:
        if not HAS_YAML:
            console.print("⚠️ PyYAML not installed. Cannot save configuration file.")
            return
            
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        console.print(f"✅ Configuration saved to {config_path}")
    except Exception as e:
        console.print(f"❌ Failed to save config to {config_path}: {e}")

def get_password_securely(prompt: str = "Enter password: ") -> str:
    """
    Get password from user securely (hidden input)
    
    Args:
        prompt: Prompt message
        
    Returns:
        Password string
    """
    return OutputFormatter.prompt(prompt, password=True)

def format_bytes(size: int) -> str:
    """
    Format bytes as human-readable string
    
    Args:
        size: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.2 KB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

def truncate_string(s: str, max_length: int = 50, ellipsis: str = "...") -> str:
    """
    Truncate string to maximum length
    
    Args:
        s: String to truncate
        max_length: Maximum length
        ellipsis: Ellipsis string to append
        
    Returns:
        Truncated string
    """
    if len(s) <= max_length:
        return s
    return s[:max_length - len(ellipsis)] + ellipsis

def create_example_config() -> str:
    """
    Create an example configuration file content
    
    Returns:
        Example YAML configuration as string
    """
    example = """# BioCypher CLI Configuration
# Copy this to ~/.biocypher.yaml and modify as needed

# Message processing limits
max_message_length: 1000
max_dna_sequence_length: 10000

# Default encoding mode: basic, nanopore, or secure
default_encoding_mode: basic

# Output format: text, json, or fasta
output_format: text

# Display settings
colors_enabled: true
progress_bars: true

# File processing
auto_detect_format: true
backup_files: false

# Security settings
password_min_length: 8
require_strong_passwords: true
"""
    return example