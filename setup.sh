#!/bin/bash

# TikTok RSS Setup Script
echo "Setting up TikTok RSS environment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if virtualenv is available, install if not
if ! python3 -m venv --help &> /dev/null; then
    echo "Installing virtualenv..."
    pip3 install virtualenv
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate

# Install playwright first (newer version to avoid greenlet compatibility issues)
pip install playwright

# Install playwright browsers
playwright install

# Install remaining dependencies
pip install asyncio feedgen TikTokApi config

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Set your MS_TOKEN environment variable:"
echo "   export MS_TOKEN=\"your_token_here\""
echo ""
echo "2. Run the script:"
echo "   ./run.sh"
echo ""
echo "Or manually:"
echo "   source venv/bin/activate"
echo "   python postprocessing.py"