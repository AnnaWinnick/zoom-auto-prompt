# Zoom Recording Prompt v1.0.0

## Overview
Zoom Recording Prompt automatically detects when you're hosting a Zoom meeting and prompts you to start recording. This application runs in the background and helps ensure your important meetings are always recorded.

## Download
- [Zoom Recording Prompt.zip](link-to-release-asset) - macOS application bundle

## Features
- Automatic detection of Zoom meetings
- Host identification
- Pop-up prompts for recording
- Snooze functionality
- Uses Zoom API with fallback to keyboard shortcuts

## Installation Instructions
1. Download the ZIP file from the link above
2. Extract the contents
3. Move `Zoom Recording Prompt.app` to your Applications folder
4. Follow the setup instructions in the README to configure your Zoom API credentials

## Requirements
- macOS 10.14 or higher
- Zoom desktop application
- Personal Zoom App credentials (see README for setup instructions)

## Setting up Zoom API Access
Before using the application, you need to create a personal Zoom API app:

1. Visit the [Zoom App Marketplace](https://marketplace.zoom.us/)
2. Click "Develop" → "Build App" → Select "Server-to-Server OAuth"
3. Name your app and create it
4. Note your Account ID, Client ID, and Client Secret
5. Add required scopes: `/meeting:read:admin`, `/meeting:write:admin`, `/recording:write:admin`
6. Create a `.env` file in your home directory with your credentials

## Changelog
- Initial release
- Native notifications
- Automatic meeting detection
- API and keyboard shortcut recording methods

## Known Issues
- None at this time

## License
MIT License - See LICENSE file for details
