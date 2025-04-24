# Zoom Recording Prompt

An automated tool for macOS that detects when you're hosting a Zoom meeting and prompts you to start recording. The application monitors Zoom meetings and provides a notification when you're the host, allowing you to start recording with a single click.

## Features

- Automatic detection of Zoom meetings
- Host identification
- Pop-up prompts for recording
- Snooze functionality
- Uses Zoom API with fallback to keyboard shortcuts

## Requirements

- macOS 10.14 or higher
- Zoom desktop application
- Personal Zoom App credentials (Server-to-Server OAuth)
- Python 3.8+ (for development only, not required for end users)

## For Users: Installation and Setup

### Option 1: Download the Pre-built Application (Recommended)

1. Download the latest release from the [Releases page](https://github.com/yourusername/zoom-auto-prompt/releases)
2. Extract the ZIP file and move `Zoom Recording Prompt.app` to your Applications folder
3. Set up your Zoom App (see instructions below)
4. Create a `.env` file in your home directory with your Zoom credentials
5. Launch the application

### Option 2: Install from Source

1. Clone the repository
```bash
git clone https://github.com/yourusername/zoom-auto-prompt.git
cd zoom-auto-prompt
```

2. Install dependencies
```bash
pip install -r requirements.txt
pip install py2app
```

3. Run the application
```bash
python zoom_recording_prompt.py
```

## Setting up your Personal Zoom App

For the application to access the Zoom API, you need to create a personal Server-to-Server OAuth app:

1. **Create a Server-to-Server OAuth App**:
   - Go to [Zoom App Marketplace](https://marketplace.zoom.us/)
   - Click "Develop" in the top-right corner
   - Click "Build App"
   - Choose "Server-to-Server OAuth" app type
   - Name your app (e.g., "Personal Recording Prompt")

2. **App Credentials**:
   - After creating the app, you'll see the following credentials:
     - Account ID
     - Client ID
     - Client Secret
   - Save these for your `.env` file

3. **Configure App Scopes**:
   - In the app settings, navigate to "Scopes"
   - Add the following scopes:
     - `/meeting:read:admin`
     - `/meeting:write:admin`
     - `/recording:write:admin`

4. **Activate App**:
   - Navigate to "App Credentials"
   - Ensure your app is activated (toggle switch should be on)
   - No publication is needed as this is for personal use

## Configuration

Create a `.env` file in your home directory:

```env
ZOOM_ACCOUNT_ID=your_account_id
ZOOM_CLIENT_ID=your_client_id
ZOOM_CLIENT_SECRET=your_client_secret
```

Replace the values with your Zoom App credentials from Step 2 above.

## Usage

1. Launch the application
2. The app will run in the background and monitor for Zoom meetings
3. When you start hosting a meeting, you'll receive a notification to start recording
4. Click "Start Recording" or use the snooze option if you want to delay recording

## For Developers: Building the macOS Application

### Prerequisites

- Python 3.8+ installed
- pip package manager
- macOS 10.14 or higher

### Building Steps

1. Install required packages:
```bash
pip install -r requirements.txt
pip install py2app
```

2. Build the application:
```bash
python setup.py py2app
```

3. The application will be built in the `dist` folder as `Zoom Recording Prompt.app`

4. To create a distributable ZIP file:
```bash
cd dist
zip -r "Zoom Recording Prompt.zip" "Zoom Recording Prompt.app"
```

### Code Signing (Optional)

For distribution outside of GitHub or personal use, you may want to sign the application:

```bash
codesign --force --deep --sign "Developer ID Application: Your Name (TEAMID)" "dist/Zoom Recording Prompt.app"
```

## Troubleshooting

### API Authentication Issues
- Verify your `.env` file contains correct credentials
- Ensure all required scopes are added to your Zoom App
- Check if your app is activated in the Zoom Marketplace

### Recording Not Starting
- API Method:
  - Check Zoom App credentials and scopes
  - Verify your account has recording privileges
- Fallback Method (AppleScript):
  - Ensure Zoom is the active window
  - Check keyboard shortcuts in Zoom settings
  - Make sure you have accessibility permissions enabled for the app

### Notifications Not Showing
- Check system notification settings
- Ensure application has necessary permissions

### App Permissions
For macOS users, you may need to:
1. Go to System Preferences > Security & Privacy > Privacy
2. Add the app to Accessibility permissions
3. Add the app to Screen Recording permissions (macOS 10.15+)

## Security Notes
- Keep your `.env` file secure and never share your credentials
- The app only has access to your personal Zoom account
- Credentials are stored locally and never transmitted to third parties

## License
MIT License - See LICENSE file for details
