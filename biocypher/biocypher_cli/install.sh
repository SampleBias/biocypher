#!/bin/bash

# BioCypher CLI Installation Script

echo "🧬 Installing BioCypher CLI..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "❌ Python 3.8 or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found"

# Install dependencies
echo "📦 Installing dependencies..."
if pip3 install -r requirements.txt; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Make CLI executable
chmod +x biocypher_cli.py

echo "🎉 BioCypher CLI installed successfully!"
echo ""
echo "🚀 Quick start:"
echo "  ./biocypher_cli.py encode \"Hello World\""
echo "  ./biocypher_cli.py --help"
echo ""
echo "📖 For full documentation, see README.md"