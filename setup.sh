#!/bin/bash

# Quick setup script for BDD Obfuscation Wrapper

set -e

echo "🚀 Setting up BDD Obfuscation Wrapper..."

# Check for uv
if ! command -v uv &> /dev/null; then
    echo "⚠️  uv not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Install dependencies with uv
echo "📦 Installing dependencies..."
uv sync --no-dev

# Check for Ollama
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama not found."
    echo "   Install from https://ollama.com/"
    echo "   Then run: ollama pull llama3.1"
else
    echo "✅ Ollama found"
    
    # Check if llama3.1 is available
    if ollama list | grep -q "llama3.1"; then
        echo "✅ llama3.1 model available"
    else
        echo "⚠️  llama3.1 model not found"
        echo "   Run: ollama pull llama3.1"
    fi
fi

# Make wrapper executable
chmod +x behave_wrapper.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run tests:"
echo "  python behave_wrapper.py"
echo ""
echo "If Ollama is not running, start it first:"
echo "  ollama serve"
echo ""