#!/bin/bash
# Script to build the macOS application bundle

echo "Building Zoom Recording Prompt macOS application..."

# Check if py2app is installed
if ! pip show py2app > /dev/null; then
  echo "py2app is not installed. Installing it now..."
  pip install py2app
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Clean any previous build artifacts
echo "Cleaning previous build artifacts..."
rm -rf build dist

# Build the application
echo "Building application bundle..."
python setup.py py2app

# Check if build was successful
if [ -d "dist/Zoom Recording Prompt.app" ]; then
  echo "Build successful! Application is located at: dist/Zoom Recording Prompt.app"

  # Create a ZIP file for distribution
  echo "Creating ZIP file for distribution..."
  cd dist
  zip -r "Zoom Recording Prompt.zip" "Zoom Recording Prompt.app"
  cd ..

  echo "ZIP file created at: dist/Zoom Recording Prompt.zip"
  echo "You can now distribute this ZIP file or use it for your personal use."
else
  echo "Build failed. Please check the error messages above."
fi

echo "Build process completed."
