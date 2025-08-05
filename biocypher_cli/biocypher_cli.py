#!/usr/bin/env python3
"""
BioCypher CLI - Advanced DNA Cryptography System
Command-line version of the BioCypher application

Author: James Utley
License: bi0cyph3r DNA Cryptography System License
"""

import sys
import os
from pathlib import Path

# Add the current directory to the Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from cli.commands import cli

def main():
    """Main entry point for BioCypher CLI"""
    try:
        cli()
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()