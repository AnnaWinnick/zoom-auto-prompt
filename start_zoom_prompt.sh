#!/bin/bash
# Script to start Zoom Recording Prompt

# Change to the directory where this script is located
cd "$(dirname "$0")"

# Check if we're running from the source or from a built app
if [ -f "zoom_recording_prompt.py" ]; then
    # Source mode - check for Python
    if command -v python3 &>/dev/null; then
        echo "Starting Zoom Recording Prompt using Python..."

        # Check for virtual environment
        if [ -d "venv" ]; then
            source venv/bin/activate
        fi

        # Run the application
        python3 zoom_recording_prompt.py
    else
        echo "Error: Python 3 is not installed. Please install Python 3 to run this application."
        exit 1
    fi
elif [ -d "dist/Zoom Recording Prompt.app" ]; then
    # Built app mode - open the app
    echo "Starting Zoom Recording Prompt application..."
    open "dist/Zoom Recording Prompt.app"
else
    echo "Error: Could not find Zoom Recording Prompt application."
    echo "Please run './build_macos.sh' first to build the application."
    exit 1
fi
