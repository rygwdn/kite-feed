#!/bin/bash
# Setup script for Cursor Background Agents

set -e

echo "Setting up Cursor Background Agents..."

# Install uv if not already installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install project dependencies
echo "Installing project dependencies..."
uv sync --dev

# Install up CLI tool for Cursor cloud agents
# Note: This may require manual installation depending on your Cursor setup
# Check https://cursor.com/docs/cloud-agent for the latest installation instructions
if ! command -v up &> /dev/null; then
    echo "Warning: 'up' CLI tool not found."
    echo "Please install it following the instructions at: https://cursor.com/docs/cloud-agent"
    echo ""
    echo "You may need to:"
    echo "1. Install Cursor IDE"
    echo "2. Install the 'up' CLI tool from within Cursor"
    echo "3. Or download it from the Cursor releases page"
fi

echo ""
echo "Setup complete!"
echo ""
echo "To use background agents:"
echo "1. Ensure 'up' CLI tool is installed"
echo "2. Configure your Cursor IDE settings"
echo "3. Use 'up' commands to manage cloud agents"
