"""
CLI command implementations for BioCypher
"""

import click
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from core.dna_crypto import DNACrypto, DNACryptoError
from core.nanopore_crypto import NanoporeDNACrypto, NanoporeDNACryptoError
from core.secure_crypto import SecureNanoporeDNACrypto, SecureDNACryptoError
from core.safety_screener import DNASafetyScreener, SafetyScreenerError

from .formatters import (
    console, DNAFormatter, SecurityFormatter, SafetyFormatter, 
    ProgressFormatter, OutputFormatter
)
from .utils import (
    detect_input_type, detect_encoding_mode, read_file_content, 
    write_file_content, validate_dna_sequence, get_password_securely,
    load_config, truncate_string
)

@click.group()
@click.version_option(version="1.0.0", prog_name="BioCypher CLI")
@click.option('--config', '-c', type=click.Path(), help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, config, verbose):
    """
    🧬 BioCypher CLI - Advanced DNA Cryptography System
    
    Convert text messages to DNA sequences and back with multiple encoding modes:
    - Basic: Simple binary-to-DNA mapping
    - Nanopore: Optimized for nanopore sequencing  
    - Secure: AES encryption + DNA encoding
    """
    # Initialize context
    ctx.ensure_object(dict)
    ctx.obj['config'] = load_config(config)
    ctx.obj['verbose'] = verbose
    
    if verbose:
        console.print("🧬 [bold green]BioCypher CLI initialized[/bold green]")

@cli.command()
@click.argument('message', required=False)
@click.option('--mode', '-m', type=click.Choice(['basic', 'nanopore', 'secure']), 
              default='basic', help='Encoding mode')
@click.option('--input-file', '-i', type=click.Path(exists=True), 
              help='Read message from file')
@click.option('--output-file', '-o', type=click.Path(), 
              help='Write DNA sequence to file')
@click.option('--password', '-p', help='Password for secure mode')
@click.option('--error-correction/--no-error-correction', default=True,
              help='Enable error correction for nanopore mode')
@click.option('--format', 'output_format', type=click.Choice(['text', 'fasta', 'json']),
              default='text', help='Output format')
@click.option('--show-stats', is_flag=True, help='Show sequence statistics')
@click.pass_context
def encode(ctx, message, mode, input_file, output_file, password, 
           error_correction, output_format, show_stats):
    """
    🧬 Encode text message into DNA sequence
    
    Examples:
      biocypher encode "Hello World"
      biocypher encode -m nanopore -i message.txt -o sequence.dna
      biocypher encode -m secure -p mypassword "Secret message"
    """
    try:
        # Get input message
        if input_file:
            message = read_file_content(input_file)
            if ctx.obj['verbose']:
                console.print(f"📖 Read message from {input_file}")
        elif message is None:
            message = OutputFormatter.prompt("Enter message to encode")
        
        if not message:
            OutputFormatter.print_error("No message provided")
            sys.exit(1)
        
        # Validate message length
        max_length = ctx.obj['config'].get('max_message_length', 1000)
        if len(message) > max_length:
            OutputFormatter.print_error(f"Message too long. Maximum {max_length} characters allowed.")
            sys.exit(1)
        
        # Handle different encoding modes
        if mode == 'secure':
            if not password:
                password = get_password_securely("Enter password for secure encoding: ")
            
            crypto = SecureNanoporeDNACrypto()
            
            # Validate password strength
            strength = crypto.validate_password_strength(password)
            if not strength['valid'] and ctx.obj['config'].get('require_strong_passwords', True):
                console.print()
                console.print(SecurityFormatter.format_password_strength(strength))
                if not OutputFormatter.confirm("Use this password anyway?", default=False):
                    sys.exit(1)
            
            with console.status("🔒 Encrypting and encoding..."):
                encoded_sequence = crypto.secure_encode_message(message, password, error_correction)
                security_info = crypto.get_security_info()
                
        elif mode == 'nanopore':
            with console.status("🧬 Encoding with nanopore optimization..."):
                encoded_sequence = NanoporeDNACrypto.encode_message(message, error_correction)
                security_info = None
                
        else:  # basic mode
            with console.status("🧬 Encoding with basic mode..."):
                encoded_sequence = DNACrypto.encode_message(message)
                security_info = None
        
        # Show results
        console.print()
        OutputFormatter.print_success(f"Message encoded successfully using {mode} mode")
        
        # Display encoded sequence
        dna_formatted = DNAFormatter.format_dna_sequence(encoded_sequence)
        console.print("\n📊 [bold]Encoded DNA Sequence:[/bold]")
        console.print(dna_formatted)
        
        # Show statistics if requested
        if show_stats:
            console.print()
            if mode == 'nanopore':
                stats = NanoporeDNACrypto.get_nanopore_stats(encoded_sequence)
            else:
                stats = DNACrypto.get_sequence_stats(encoded_sequence)
            
            console.print(DNAFormatter.format_sequence_stats(stats))
        
        # Show security info for secure mode
        if security_info:
            console.print()
            console.print(SecurityFormatter.format_security_info(security_info))
        
        # Save to file if requested
        if output_file:
            write_file_content(output_file, encoded_sequence, output_format)
            console.print(f"\n💾 DNA sequence saved to {output_file}")
        
        console.print(f"\n📏 Sequence length: {len(encoded_sequence):,} bases")
        console.print(f"📝 Original message: {truncate_string(message, 50)}")
        
    except (DNACryptoError, NanoporeDNACryptoError, SecureDNACryptoError) as e:
        OutputFormatter.print_error("Encoding failed", str(e))
        sys.exit(1)
    except Exception as e:
        OutputFormatter.print_error("Unexpected error", str(e))
        if ctx.obj['verbose']:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)

@cli.command()
@click.argument('sequence', required=False)
@click.option('--mode', '-m', type=click.Choice(['basic', 'nanopore', 'secure', 'auto']),
              default='auto', help='Decoding mode (auto-detect if not specified)')
@click.option('--input-file', '-i', type=click.Path(exists=True),
              help='Read DNA sequence from file')
@click.option('--output-file', '-o', type=click.Path(),
              help='Write decoded message to file')
@click.option('--password', '-p', help='Password for secure mode')
@click.option('--error-correction/--no-error-correction', default=True,
              help='Enable error correction for nanopore mode')
@click.option('--show-stats', is_flag=True, help='Show sequence statistics')
@click.pass_context
def decode(ctx, sequence, mode, input_file, output_file, password, 
           error_correction, show_stats):
    """
    🧬 Decode DNA sequence back to text message
    
    Examples:
      biocypher decode "ATCGATCG..."
      biocypher decode -i sequence.dna -o message.txt
      biocypher decode -m secure -p mypassword "ATCGATCG..."
    """
    try:
        # Get input sequence
        if input_file:
            sequence = read_file_content(input_file)
            if ctx.obj['verbose']:
                console.print(f"📖 Read sequence from {input_file}")
        elif sequence is None:
            sequence = OutputFormatter.prompt("Enter DNA sequence to decode")
        
        if not sequence:
            OutputFormatter.print_error("No DNA sequence provided")
            sys.exit(1)
        
        # Validate sequence
        is_valid, error_msg = validate_dna_sequence(sequence)
        if not is_valid:
            OutputFormatter.print_error("Invalid DNA sequence", error_msg)
            sys.exit(1)
        
        # Auto-detect mode if needed
        if mode == 'auto':
            mode = detect_encoding_mode(sequence)
            if ctx.obj['verbose']:
                console.print(f"🔍 Auto-detected encoding mode: {mode}")
        
        # Handle different decoding modes
        if mode == 'secure':
            if not password:
                password = get_password_securely("Enter password for secure decoding: ")
            
            crypto = SecureNanoporeDNACrypto()
            with console.status("🔓 Decrypting and decoding..."):
                decoded_message = crypto.secure_decode_sequence(sequence, password, error_correction)
                
        elif mode == 'nanopore':
            with console.status("🧬 Decoding nanopore sequence..."):
                decoded_message = NanoporeDNACrypto.decode_sequence(sequence, error_correction)
                
        else:  # basic mode
            with console.status("🧬 Decoding basic sequence..."):
                decoded_message = DNACrypto.decode_sequence(sequence)
        
        if not decoded_message:
            OutputFormatter.print_error("Decoding failed", "No message could be extracted from the sequence")
            sys.exit(1)
        
        # Show results
        console.print()
        OutputFormatter.print_success(f"DNA sequence decoded successfully using {mode} mode")
        
        # Display decoded message
        console.print(f"\n📝 [bold]Decoded Message:[/bold]")
        console.print(f"[green]{decoded_message}[/green]")
        
        # Show statistics if requested
        if show_stats:
            console.print()
            if mode == 'nanopore':
                stats = NanoporeDNACrypto.get_nanopore_stats(sequence)
            else:
                stats = DNACrypto.get_sequence_stats(sequence)
            
            console.print(DNAFormatter.format_sequence_stats(stats))
        
        # Save to file if requested
        if output_file:
            write_file_content(output_file, decoded_message, 'text')
            console.print(f"\n💾 Message saved to {output_file}")
        
        console.print(f"\n📏 Original sequence length: {len(sequence):,} bases")
        console.print(f"📝 Message length: {len(decoded_message)} characters")
        
    except (DNACryptoError, NanoporeDNACryptoError, SecureDNACryptoError) as e:
        OutputFormatter.print_error("Decoding failed", str(e))
        sys.exit(1)
    except Exception as e:
        OutputFormatter.print_error("Unexpected error", str(e))
        if ctx.obj['verbose']:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)

@cli.command()
@click.argument('sequence', required=False)
@click.option('--input-file', '-i', type=click.Path(exists=True),
              help='Read DNA sequence from file')
@click.option('--mode', '-m', type=click.Choice(['basic', 'nanopore']),
              default='nanopore', help='Analysis mode')
@click.pass_context
def analyze(ctx, sequence, input_file, mode):
    """
    📊 Analyze DNA sequence characteristics and optimization
    
    Examples:
      biocypher analyze "ATCGATCG..."
      biocypher analyze -i sequence.dna
      biocypher analyze -m nanopore "ATCGATCG..."
    """
    try:
        # Get input sequence
        if input_file:
            sequence = read_file_content(input_file)
            if ctx.obj['verbose']:
                console.print(f"📖 Read sequence from {input_file}")
        elif sequence is None:
            sequence = OutputFormatter.prompt("Enter DNA sequence to analyze")
        
        if not sequence:
            OutputFormatter.print_error("No DNA sequence provided")
            sys.exit(1)
        
        # Validate sequence
        is_valid, error_msg = validate_dna_sequence(sequence)
        if not is_valid:
            OutputFormatter.print_error("Invalid DNA sequence", error_msg)
            sys.exit(1)
        
        with console.status("📊 Analyzing sequence..."):
            if mode == 'nanopore':
                stats = NanoporeDNACrypto.get_nanopore_stats(sequence)
            else:
                stats = DNACrypto.get_sequence_stats(sequence)
        
        # Display results
        console.print()
        console.print(f"📊 [bold]DNA Sequence Analysis ({mode} mode)[/bold]")
        
        # Show formatted sequence (truncated if too long)
        if len(sequence) <= 200:
            dna_formatted = DNAFormatter.format_dna_sequence(sequence)
            console.print("\n🧬 [bold]Sequence:[/bold]")
            console.print(dna_formatted)
        else:
            # Show first and last parts
            start_seq = DNAFormatter.format_dna_sequence(sequence[:100])
            end_seq = DNAFormatter.format_dna_sequence(sequence[-100:])
            console.print("\n🧬 [bold]Sequence (first 100 bases):[/bold]")
            console.print(start_seq)
            console.print("\n... [truncated] ...")
            console.print("\n🧬 [bold]Sequence (last 100 bases):[/bold]")
            console.print(end_seq)
        
        # Show statistics
        console.print()
        console.print(DNAFormatter.format_sequence_stats(stats))
        
        # Show nanopore-specific analysis
        if mode == 'nanopore' and 'nanopore_optimized' in stats:
            console.print()
            optimized = stats['nanopore_optimized']
            risk_score = stats.get('nanopore_risk_score', 0)
            
            if optimized:
                console.print("✅ [green]Sequence is optimized for nanopore sequencing[/green]")
            else:
                console.print("⚠️ [yellow]Sequence may have issues with nanopore sequencing[/yellow]")
                console.print(f"   Risk score: {risk_score}")
            
            # Show warnings
            warnings = stats.get('warnings', [])
            if warnings:
                console.print("\n⚠️ [yellow]Warnings:[/yellow]")
                for warning in warnings:
                    console.print(f"   • {warning}")
            
            # Show homopolymers
            homopolymers = stats.get('homopolymers', [])
            if homopolymers:
                console.print(f"\n🧬 Found {len(homopolymers)} homopolymer runs:")
                for base, length, position in homopolymers[:5]:  # Show first 5
                    console.print(f"   • {length}x {base} at position {position}")
                if len(homopolymers) > 5:
                    console.print(f"   ... and {len(homopolymers) - 5} more")
        
    except Exception as e:
        OutputFormatter.print_error("Analysis failed", str(e))
        if ctx.obj['verbose']:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)

@cli.command()
@click.argument('sequence', required=False)
@click.option('--input-file', '-i', type=click.Path(exists=True),
              help='Read DNA sequence from file')
@click.pass_context
def safety(ctx, sequence, input_file):
    """
    🛡️ Perform comprehensive safety screening of DNA sequence
    
    Examples:
      biocypher safety "ATCGATCG..."
      biocypher safety -i sequence.dna
    """
    try:
        # Get input sequence
        if input_file:
            sequence = read_file_content(input_file)
            if ctx.obj['verbose']:
                console.print(f"📖 Read sequence from {input_file}")
        elif sequence is None:
            sequence = OutputFormatter.prompt("Enter DNA sequence for safety screening")
        
        if not sequence:
            OutputFormatter.print_error("No DNA sequence provided")
            sys.exit(1)
        
        with console.status("🛡️ Performing safety screening..."):
            report = DNASafetyScreener.perform_comprehensive_screening(sequence)
        
        # Display safety report
        console.print()
        SafetyFormatter.format_safety_report(report)
        
    except SafetyScreenerError as e:
        OutputFormatter.print_error("Safety screening failed", str(e))
        sys.exit(1)
    except Exception as e:
        OutputFormatter.print_error("Unexpected error", str(e))
        if ctx.obj['verbose']:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)

@cli.group()
def password():
    """🔐 Password utilities for secure mode"""
    pass

@password.command('generate')
@click.option('--length', '-l', default=16, help='Password length (minimum 12)')
@click.option('--count', '-c', default=1, help='Number of passwords to generate')
def generate_password(length, count):
    """Generate cryptographically secure passwords"""
    try:
        console.print(f"🔐 [bold]Generated Password{'s' if count > 1 else ''}:[/bold]")
        
        for i in range(count):
            password = SecureNanoporeDNACrypto.generate_secure_password(length)
            strength = SecureNanoporeDNACrypto().validate_password_strength(password)
            
            console.print(f"\n{i+1}. [green]{password}[/green]")
            console.print(f"   Strength: {strength['strength']} ({strength['score']}/{strength['max_score']})")
            
    except Exception as e:
        OutputFormatter.print_error("Password generation failed", str(e))
        sys.exit(1)

@password.command('check')
@click.argument('password', required=False)
def check_password(password):
    """Check password strength"""
    try:
        if not password:
            password = get_password_securely("Enter password to check: ")
        
        crypto = SecureNanoporeDNACrypto()
        strength = crypto.validate_password_strength(password)
        
        console.print()
        console.print(SecurityFormatter.format_password_strength(strength))
        
    except Exception as e:
        OutputFormatter.print_error("Password check failed", str(e))
        sys.exit(1)

@cli.command()
@click.argument('sequence', required=False)
@click.option('--input-file', '-i', type=click.Path(exists=True),
              help='Read DNA sequence from file')
@click.pass_context
def validate(ctx, sequence, input_file):
    """✅ Validate DNA sequence format and structure"""
    try:
        # Get input sequence
        if input_file:
            sequence = read_file_content(input_file)
            console.print(f"📖 Read sequence from {input_file}")
        elif sequence is None:
            sequence = OutputFormatter.prompt("Enter DNA sequence to validate")
        
        if not sequence:
            OutputFormatter.print_error("No DNA sequence provided")
            sys.exit(1)
        
        # Perform validation
        is_valid, error_msg = validate_dna_sequence(sequence)
        
        if is_valid:
            console.print("✅ [green]DNA sequence is valid[/green]")
            console.print(f"📏 Length: {len(sequence):,} bases")
            
            # Try to detect encoding mode
            detected_mode = detect_encoding_mode(sequence)
            console.print(f"🔍 Detected encoding mode: {detected_mode}")
            
        else:
            OutputFormatter.print_error("Invalid DNA sequence", error_msg)
            sys.exit(1)
            
    except Exception as e:
        OutputFormatter.print_error("Validation failed", str(e))
        sys.exit(1)

if __name__ == '__main__':
    cli()