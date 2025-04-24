# Zoom Recording Prompt

An automated tool for macOS that detects when you're hosting a Zoom meetings and prompts you to start recording. The application monitors your Zoom client and sends notifications when you're the host, allowing you to start recording with a single click.

## Features

- Automatic detection of Zoom meetings
- Host identification
- Pop-up prompts for recording
- Snooze functionality (delay recording reminders)
- Uses Zoom API with fallback to keyboard shortcuts

## Requirements

- macOS 10.14 or higher
- Python 3.8+
- Zoom desktop application
- Personal Zoom App credentials (Server-to-Server OAuth)

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/AnnaWinnick/zoom-auto-prompt.git
cd zoom-auto-prompt
```

### 2. Set Up a Virtual Environment

Creating a virtual environment keeps your dependencies isolated:

```bash
# Create a new virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a Zoom API App

To use the script, you need your own Zoom API credentials:

1. Go to the [Zoom App Marketplace](https://marketplace.zoom.us/)
2. Click "Develop" in the top-right corner
3. Click "Build App"
4. Select "Server-to-Server OAuth" app type
5. Name your app (e.g., "Recording Prompt")
6. Under "App Credentials", note your:
   - Account ID
   - Client ID
   - Client Secret
7. Go to "Scopes" and add these permissions:
   - `/meeting:read:admin`
   - `/meeting:write:admin`
   - `/recording:write:admin`
8. Make sure your app is activated (toggle switch is ON)

### 5. Configure Environment Variables

Create a `.env` file in the project root directory:

```bash
# Create the .env file
touch .env

# Open it in your text editor
# On macOS:
open -a TextEdit .env
# Or use any text editor you prefer
```

Add your Zoom credentials to the file:

```
ZOOM_ACCOUNT_ID=your_account_id_here
ZOOM_CLIENT_ID=your_client_id_here
ZOOM_CLIENT_SECRET=your_client_secret_here
```

### 6. Run the Script

```bash
# Make sure your virtual environment is activated
source venv/bin/activate

# Run the script
python zoom_recording_prompt.py
```

## Usage

Once running, the application:

1. Monitors for active Zoom meetings
2. When you're hosting a meeting, displays a prompt to start recording
3. Allows you to:
   - Start recording immediately
   - Snooze the reminder
   - Dismiss the prompt

The application runs in the background and will check for meetings every few seconds.

## Troubleshooting

### API Authentication Issues
- Verify your `.env` file contains the correct credentials
- Check that all required scopes are added to your Zoom App
- Ensure your app is activated in the Zoom Marketplace

### Recording Not Starting
- API Method:
  - Check Zoom App credentials and scopes
  - Verify your account has recording privileges
- Fallback Method:
  - Ensure Zoom is the active window
  - Check keyboard shortcuts in Zoom settings

### No Notifications
- Ensure your system allows notifications from Python applications
- Check the logs for any error messages

## License
MIT License
