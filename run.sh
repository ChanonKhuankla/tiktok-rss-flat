#!/bin/bash

# TikTok RSS Run Script
echo "🚀 TikTok RSS Generator"
echo "======================"

# Check if MS_TOKEN is set
if [ -z "$MS_TOKEN" ]; then
    echo "❌ Error: MS_TOKEN environment variable is not set."
    echo ""
    echo "To get your MS_TOKEN:"
    echo "1. Log into TikTok on Chrome desktop"
    echo "2. View a user profile of someone you follow"
    echo "3. Open Chrome DevTools with F12"
    echo "4. Go to Application Tab > Storage > Cookies > https://www.tiktok.com"
    echo "5. Copy the cookie value of 'msToken'"
    echo ""
    echo "Then set it with: export MS_TOKEN=\"your_token_here\""
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run the postprocessing script
echo "Generating RSS feeds..."
python postprocessing.py

# Check if git repository is initialized
if [ -d ".git" ]; then
    echo "Committing changes to git..."
    git add .
    git commit -m "latest RSS $(date)"
    
    # Ask user if they want to push
    read -p "Do you want to push to origin main? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push origin main
        echo "Changes pushed to remote repository."
    else
        echo "Changes committed locally but not pushed."
    fi
else
    echo "Not a git repository - skipping git operations."
fi

echo "Done!"