import sys
import os
import psutil
import pyautogui
import requests
import logging
from datetime import datetime, timedelta, UTC
from collections import deque
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QPushButton, QLabel, QSpinBox, QHBoxLayout,
                            QButtonGroup, QRadioButton, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer
from dotenv import load_dotenv
import base64

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('zoom_prompt.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ZoomAPI:
    def __init__(self):
        load_dotenv()
        self.account_id = os.getenv('ZOOM_ACCOUNT_ID')
        self.client_id = os.getenv('ZOOM_CLIENT_ID')
        self.client_secret = os.getenv('ZOOM_CLIENT_SECRET')
        self.base_url = "https://api.zoom.us/v2"
        self.token_url = "https://zoom.us/oauth/token"
        self.access_token = None
        self.token_expiry = None
        logger.info("ZoomAPI initialized with account_id: %s", self.account_id)

    def get_access_token(self):
        """Get access token using Server-to-Server OAuth"""
        if self.access_token and datetime.now(UTC) < self.token_expiry:
            return self.access_token

        logger.info("Requesting new access token")
        try:
            # Base64 encode the client_id:client_secret
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()

            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            data = {
                "grant_type": "account_credentials",
                "account_id": self.account_id
            }

            response = requests.post(
                self.token_url,
                headers=headers,
                data=data
            )

            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                # Set expiry to 1 hour from now (standard OAuth token lifetime)
                self.token_expiry = datetime.now(UTC) + timedelta(seconds=token_data.get('expires_in', 3600))
                logger.info("Successfully obtained new access token")
                return self.access_token
            else:
                logger.error("Failed to get access token. Status: %s, Response: %s",
                           response.status_code, response.text)
                return None
        except Exception as e:
            logger.error("Error getting access token: %s", str(e))
            return None

    def get_meetings(self):
        """Get list of meetings for the account"""
        logger.info("Fetching meetings from Zoom API")
        access_token = self.get_access_token()
        if not access_token:
            logger.error("Failed to get valid access token")
            return {}

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.get(
                f"{self.base_url}/users/me/meetings",
                headers=headers
            )

            if response.status_code == 401:
                error_msg = response.json().get('message', 'Unknown error')
                logger.error("Authentication Error (401): %s", error_msg)
                return {}

            if response.status_code != 200:
                logger.error("API Error: %s", response.text)
            return response.json()
        except Exception as e:
            logger.error("Error fetching meetings: %s", str(e))
            return {}

    def start_recording(self, meeting_id):
        """Start recording for a specific meeting"""
        logger.info("Attempting to start recording for meeting: %s", meeting_id)
        access_token = self.get_access_token()
        if not access_token:
            logger.error("Failed to get valid access token")
            return False

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        try:
            # First, enable recording settings
            settings_response = requests.patch(
                f"{self.base_url}/meetings/{meeting_id}/recordings/settings",
                headers=headers,
                json={"recording": {"local_recording": True}}
            )

            if settings_response.status_code != 204:
                logger.error("Failed to enable recording settings: %s", settings_response.text)
                return False

            # Then, start the recording
            response = requests.put(
                f"{self.base_url}/meetings/{meeting_id}/recordings/status",
                headers=headers,
                json={"action": "start"}
            )

            if response.status_code == 401:
                error_msg = response.json().get('message', 'Unknown error')
                logger.error("Authentication Error (401): %s", error_msg)
                return False

            return response.status_code == 204
        except Exception as e:
            logger.error("Error starting recording: %s", str(e))
            return False

    def get_meeting_status(self, meeting_id):
        """Get current status of a specific meeting"""
        access_token = self.get_access_token()
        if not access_token:
            logger.error("Failed to get valid access token")
            return None

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.get(
                f"{self.base_url}/meetings/{meeting_id}",
                headers=headers
            )

            if response.status_code == 200:
                meeting_data = response.json()
                return meeting_data
            else:
                logger.error("Failed to get meeting status: %s", response.text)
                return None
        except Exception as e:
            logger.error("Error getting meeting status: %s", str(e))
            return None

class ZoomRecordingPrompt(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.info("Initializing ZoomRecordingPrompt")
        self.setFixedSize(400, 240)
        # Set window flags to keep on top
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        # Apply macOS-like styling to the window
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f7;
                color: #1d1d1f;
            }
        """)

        # Initialize Zoom API
        self.zoom_api = ZoomAPI()

        # Store recently prompted meetings
        self.prompted_meetings = deque(maxlen=5)
        # Store snoozed meetings and their expiry times
        self.snoozed_meetings = {}

        # Define a max datetime with timezone for 'wait for all' feature
        self.datetime_max_aware = datetime.max.replace(tzinfo=UTC)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        # Title label
        self.title_label = QLabel("Would you like to record this meeting?")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            font-family: -apple-system, 'SF Pro Display', 'SF Pro Text', system-ui;
            font-size: 14px;
            font-weight: 600;
            color: #1d1d1f;
        """)
        layout.addWidget(self.title_label)

        # First row: Yes and No buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 5, 0, 5)

        self.yes_button = QPushButton("Yes")
        self.no_button = QPushButton("No")

        # Make both buttons equal width
        self.yes_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.no_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Apple-style button styling
        apple_button_base = """
            QPushButton {
                font-family: -apple-system, 'SF Pro Text', system-ui;
                font-size: 12px;
                font-weight: 500;
                border-radius: 5px;
                padding: 0px 0px;
                min-width: 80px;
                min-height: 30px;  /* Increase height */
            }
        """

        primary_button = apple_button_base + """
            QPushButton {
                background-color: #0071e3;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #0077ed;
            }
            QPushButton:pressed {
                background-color: #0068d1;
            }
        """

        secondary_button = apple_button_base + """
            QPushButton {
                background-color: #e3e3e3;
                color: #1d1d1f;
                border: none;
            }
            QPushButton:hover {
                background-color: #d9d9d9;
            }
            QPushButton:pressed {
                background-color: #c9c9c9;
            }
        """

        self.yes_button.setStyleSheet(primary_button)
        self.no_button.setStyleSheet(secondary_button)

        self.yes_button.clicked.connect(self.start_recording)
        self.no_button.clicked.connect(self.hide)

        # No stretching - buttons will take up full width
        button_layout.addWidget(self.yes_button)
        button_layout.addWidget(self.no_button)
        layout.addLayout(button_layout)

        # Add specific spacing between buttons and snooze options
        spacer = QSpacerItem(20, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        layout.addItem(spacer)

        # Second row: Snooze controls with radio buttons
        snooze_layout = QVBoxLayout()
        snooze_layout.setSpacing(6)

        # Radio button group
        self.snooze_option_group = QButtonGroup(self)

        # Radio button layout (horizontal to put both options on same line)
        radio_layout = QHBoxLayout()
        radio_layout.setSpacing(10)

        # Option 1: Snooze for X minutes (left side)
        minutes_layout = QHBoxLayout()
        minutes_layout.setSpacing(6)
        self.minutes_radio = QRadioButton("Snooze for")
        self.minutes_radio.setChecked(True)  # Default selected
        self.minutes_radio.setStyleSheet("""
            font-family: -apple-system, 'SF Pro Text', system-ui;
            font-size: 12px;
        """)

        self.snooze_spinbox = QSpinBox()
        self.snooze_spinbox.setRange(1, 60)
        self.snooze_spinbox.setValue(int(os.getenv('DEFAULT_SNOOZE_TIME', 2)))
        self.snooze_spinbox.setSuffix("")
        self.snooze_spinbox.setStyleSheet("""
            QSpinBox {
                font-family: -apple-system, 'SF Pro Text', system-ui;
                font-size: 12px;
                border: 1px solid #d2d2d7;
                border-radius: 4px;
                padding: 3px 6px;
                background-color: white;
                min-height: 24px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                border: none;
                width: 14px;
                border-radius: 2px;
                background-color: #f5f5f7;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #e3e3e3;
            }
            QSpinBox::up-arrow {
                width: 6px;
                height: 6px;
            }
            QSpinBox::down-arrow {
                width: 6px;
                height: 6px;
            }
        """)

        # Add "minutes" label after the spinbox
        minutes_label = QLabel("minutes")
        minutes_label.setStyleSheet("""
            font-family: -apple-system, 'SF Pro Text', system-ui;
            font-size: 12px;
        """)

        minutes_layout.addWidget(self.minutes_radio)
        minutes_layout.addWidget(self.snooze_spinbox)
        minutes_layout.addWidget(minutes_label)

        # Option 2: Wait for all members (right side)
        self.wait_members_radio = QRadioButton("Snooze until all join")
        self.wait_members_radio.setStyleSheet("""
            font-family: -apple-system, 'SF Pro Text', system-ui;
            font-size: 12px;
        """)

        # Add both options to the horizontal layout
        radio_layout.addLayout(minutes_layout)
        radio_layout.addStretch(1)  # Add flexible space between options
        radio_layout.addWidget(self.wait_members_radio)

        # Add radio buttons to the group
        self.snooze_option_group.addButton(self.minutes_radio, 1)
        self.snooze_option_group.addButton(self.wait_members_radio, 2)

        # Add the radio layout to the main snooze layout
        snooze_layout.addLayout(radio_layout)

        # Snooze button - long and skinny across the bottom
        self.snooze_button = QPushButton("Snooze")
        self.snooze_button.setStyleSheet(secondary_button + """
            QPushButton {
                min-height: 24px;
                margin-top: 5px;
            }
        """)
        self.snooze_button.clicked.connect(self.snooze)

        # Use a full-width layout without stretches for the button
        snooze_layout.addWidget(self.snooze_button)

        # Add bottom padding below the snooze button
        bottom_spacer = QSpacerItem(20, 6, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        snooze_layout.addItem(bottom_spacer)

        layout.addLayout(snooze_layout)

        # Timer for checking Zoom status
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_zoom_status)
        check_interval = int(os.getenv('CHECK_INTERVAL', 5)) * 1000  # Convert to milliseconds
        self.check_timer.start(check_interval)
        logger.info("Check timer started with interval: %s ms", check_interval)

        # Store current meeting ID
        self.current_meeting_id = None

        # Start with window hidden
        self.hide()

    def check_zoom_status(self):
        """Check if Zoom is running and user is host"""
        try:
            # Check if Zoom process is running
            zoom_running = False

            # Different process names for different platforms
            zoom_process_names = ['zoom.us', 'Zoom', 'Zoom.exe', 'CptHost.exe']

            for proc in psutil.process_iter(['name']):
                if proc.info['name'] in zoom_process_names:
                    zoom_running = True
                    break

            # Additional check for macOS
            if not zoom_running and sys.platform == 'darwin':
                try:
                    import subprocess
                    result = subprocess.run(
                        ["pgrep", "-f", "zoom.us"],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        zoom_running = True
                except Exception as e:
                    logger.error(f"Error checking for Zoom with pgrep: {str(e)}")

            if not zoom_running:
                if self.isVisible():
                    self.hide()
                return

            # Get current meetings
            meetings = self.zoom_api.get_meetings()

            # Clean up expired snoozed meetings
            current_time = datetime.now(UTC)
            expired_snoozes = [meeting_id for meeting_id, expiry_time in self.snoozed_meetings.items()
                             if current_time > expiry_time and expiry_time != self.datetime_max_aware]

            # Check for "wait for all members" snoozed meetings
            for meeting_id, expiry_time in list(self.snoozed_meetings.items()):
                if expiry_time == self.datetime_max_aware:
                    # This is a "wait for all members" snooze
                    meeting_status = self.zoom_api.get_meeting_status(meeting_id)

                    # Check if we can get participant data
                    if meeting_status and meeting_status.get('status') == 'started':
                        try:
                            # Get participants for this meeting
                            headers = {
                                "Authorization": f"Bearer {self.zoom_api.get_access_token()}",
                                "Content-Type": "application/json"
                            }

                            response = requests.get(
                                f"{self.zoom_api.base_url}/meetings/{meeting_id}/metrics/participants",
                                headers=headers
                            )

                            if response.status_code == 200:
                                participants_data = response.json()
                                participants_joined = set()

                                # Extract participant emails
                                if 'participants' in participants_data:
                                    for participant in participants_data['participants']:
                                        if participant.get('email'):
                                            participants_joined.add(participant['email'])

                                # Get expected participants
                                expected_response = requests.get(
                                    f"{self.zoom_api.base_url}/meetings/{meeting_id}",
                                    headers=headers
                                )

                                if expected_response.status_code == 200:
                                    meeting_details = expected_response.json()
                                    required_participants = set()

                                    # Extract required participants (non-optional)
                                    if 'settings' in meeting_details and 'meeting_invitees' in meeting_details['settings']:
                                        for invitee in meeting_details['settings']['meeting_invitees']:
                                            if not invitee.get('optional', False) and invitee.get('email'):
                                                required_participants.add(invitee['email'])

                                    # Log the expected and current participants
                                    logger.info(f"Meeting {meeting_id}: Required participants: {sorted(list(required_participants))}")
                                    logger.info(f"Meeting {meeting_id}: Current participants: {sorted(list(participants_joined))}")

                                    # Determine who is missing
                                    missing_participants = required_participants - participants_joined
                                    if missing_participants:
                                        logger.info(f"Meeting {meeting_id}: Still waiting for: {sorted(list(missing_participants))}")
                                    else:
                                        # No one is missing or no required participants found
                                        logger.info(f"Meeting {meeting_id}: No missing participants, removing from snoozed to re-prompt")
                                        expired_snoozes.append(meeting_id)
                                        # Remove from prompted meetings as well to ensure it's re-prompted
                                        if meeting_id in self.prompted_meetings:
                                            self.prompted_meetings.remove(meeting_id)

                                    # If all required participants have joined, remove from snoozed
                                    if required_participants and required_participants.issubset(participants_joined):
                                        logger.info("All required participants joined meeting %s, removing from snoozed", meeting_id)
                                        expired_snoozes.append(meeting_id)
                                else:
                                    # If we can't get expected participants, remove from snoozed to re-prompt
                                    logger.info(f"Meeting {meeting_id}: Could not get expected participants, removing from snoozed to re-prompt")
                                    expired_snoozes.append(meeting_id)
                                    if meeting_id in self.prompted_meetings:
                                        self.prompted_meetings.remove(meeting_id)
                            else:
                                # If we can't get current participants, remove from snoozed to re-prompt
                                logger.info(f"Meeting {meeting_id}: Could not get current participants, removing from snoozed to re-prompt")
                                expired_snoozes.append(meeting_id)
                                if meeting_id in self.prompted_meetings:
                                    self.prompted_meetings.remove(meeting_id)
                        except Exception as e:
                            logger.error("Error checking participants for meeting %s: %s", meeting_id, str(e))
                            # If there's an error, remove from snoozed to re-prompt
                            logger.info(f"Meeting {meeting_id}: Error checking participants, removing from snoozed to re-prompt")
                            expired_snoozes.append(meeting_id)
                            if meeting_id in self.prompted_meetings:
                                self.prompted_meetings.remove(meeting_id)

            for meeting_id in expired_snoozes:
                del self.snoozed_meetings[meeting_id]

            if 'meetings' in meetings:
                active_meeting = False
                for meeting in meetings['meetings']:
                    meeting_id = meeting['id']
                    meeting_status = self.zoom_api.get_meeting_status(meeting_id)

                    if meeting_status and meeting_status.get('status') == 'started':
                        self.current_meeting_id = meeting_id
                        active_meeting = True

                        # Check if meeting has been prompted or is snoozed
                        if (meeting_id not in self.prompted_meetings and
                            meeting_id not in self.snoozed_meetings):
                            if not self.isVisible():
                                # Center the window on the screen
                                screen = QApplication.primaryScreen().geometry()
                                self.move(
                                    screen.center().x() - self.width() // 2,
                                    screen.center().y() - self.height() // 2
                                )
                                self.show()
                                # Add to prompted meetings only when showing the window
                                self.prompted_meetings.append(meeting_id)
                        break

                if not active_meeting and self.isVisible():
                    self.hide()
            else:
                if self.isVisible():
                    self.hide()

        except Exception as e:
            logger.error("Error in check_zoom_status: %s", str(e))
            if self.isVisible():
                self.hide()

    def snooze(self):
        """Snooze the prompt based on selected option"""
        if not self.current_meeting_id:
            self.hide()
            return

        if self.minutes_radio.isChecked():
            # Option 1: Snooze for X minutes
            snooze_minutes = self.snooze_spinbox.value()
            logger.info("User snoozed meeting %s for %s minutes",
                      self.current_meeting_id, snooze_minutes)
            # Store snooze expiry time
            self.snoozed_meetings[self.current_meeting_id] = (
                datetime.now(UTC) + timedelta(minutes=snooze_minutes)
            )
        else:
            # Option 2: Wait for all members
            logger.info("User snoozed meeting %s until all members join", self.current_meeting_id)

            # Get meeting details to log expected participants
            try:
                # Get access token
                access_token = self.zoom_api.get_access_token()
                if access_token:
                    headers = {
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    }

                    # Get meeting details
                    response = requests.get(
                        f"{self.zoom_api.base_url}/meetings/{self.current_meeting_id}",
                        headers=headers
                    )

                    if response.status_code == 200:
                        meeting_details = response.json()
                        required_participants = []

                        # Extract required participants (non-optional)
                        if 'settings' in meeting_details and 'meeting_invitees' in meeting_details['settings']:
                            for invitee in meeting_details['settings']['meeting_invitees']:
                                if not invitee.get('optional', False) and invitee.get('email'):
                                    required_participants.append(invitee['email'])

                        if required_participants:
                            logger.info("Meeting %s: Waiting for these required participants: %s",
                                       self.current_meeting_id, required_participants)
                        else:
                            logger.info("Meeting %s: No required participants found in meeting settings",
                                       self.current_meeting_id)
            except Exception as e:
                logger.error("Error getting required participants for meeting %s: %s",
                            self.current_meeting_id, str(e))

            # Use a timezone-aware datetime.max to indicate waiting for all members
            self.snoozed_meetings[self.current_meeting_id] = self.datetime_max_aware

        # Remove from prompted meetings so it can be re-prompted after snooze
        if self.current_meeting_id in self.prompted_meetings:
            self.prompted_meetings.remove(self.current_meeting_id)

        self.hide()

    def start_recording(self):
        """Start recording the Zoom meeting"""
        try:
            if self.current_meeting_id:
                logger.info("User requested to start recording for meeting: %s", self.current_meeting_id)

                # First check if meeting is in progress
                meeting_status = self.zoom_api.get_meeting_status(self.current_meeting_id)
                if not meeting_status or meeting_status.get('status') != 'started':
                    logger.error("Meeting is not in progress, cannot start recording")
                    self.show_notification("Recording Error", "Meeting is not in progress. Cannot start recording.")
                    self.hide()
                    return

                # Try using Zoom API first
                if os.getenv('ENABLE_API', 'true').lower() == 'true':
                    # Try to start recording using API
                    headers = {
                        "Authorization": f"Bearer {self.zoom_api.get_access_token()}",
                        "Content-Type": "application/json"
                    }

                    # Try to start recording directly
                    response = requests.post(
                        f"{self.zoom_api.base_url}/live_meetings/{self.current_meeting_id}/events",
                        headers=headers,
                        json={"event": "recording.start", "setting": {"recording_type": "cloud"}}
                    )

                    if response.status_code in [200, 201, 202, 204]:
                        logger.info("Recording started successfully via API")
                        self.show_notification("Recording Started", "Your Zoom meeting is now being recorded.")
                        self.hide()
                        return
                    else:
                        logger.error("Failed to start recording: %s", response.text)
                        # Fall back to keyboard shortcuts
                        self._execute_recording_keystrokes()
                        self.show_notification("Recording Started", "Recording started using keyboard shortcut.")
                else:
                    # API not enabled, use keyboard shortcut
                    self._execute_recording_keystrokes()
                    self.show_notification("Recording Started", "Recording started using keyboard shortcut.")
        except Exception as e:
            logger.error("Error starting recording: %s", str(e))
            # Fallback to keyboard shortcut
            self._execute_recording_keystrokes()
            self.show_notification("Recording Started", "Recording started using keyboard shortcut.")
        self.hide()

    def _execute_recording_keystrokes(self):
        """Execute the keyboard shortcuts for recording based on OS"""
        try:
            logger.info("Using keyboard shortcut fallback")

            # Execute keystrokes based on OS
            if sys.platform == 'darwin':  # macOS
                logger.info("Executing macOS keyboard shortcuts for recording")
                # Use AppleScript to send keystrokes - more reliable on macOS
                self._send_mac_keystrokes_via_applescript()
            else:  # Windows
                logger.info("Executing Windows keyboard shortcut: Alt+R")
                try:
                    pyautogui.hotkey('alt', 'r')
                except Exception as e:
                    logger.error("Error with pyautogui hotkey: %s", str(e))

            # Log success
            logger.info("Keyboard shortcuts executed successfully")

        except Exception as e:
            logger.error("Error executing keyboard shortcut: %s", str(e))

    def _send_mac_keystrokes_via_applescript(self):
        """Use AppleScript to send keystrokes on macOS (more reliable)"""
        try:
            import subprocess

            # First make sure Zoom is activated
            activate_script = 'tell application "zoom.us" to activate'
            subprocess.run(["osascript", "-e", activate_script], check=False)

            # Send Command+Shift+R keystroke via AppleScript
            cmd_shift_r_script = '''
            tell application "System Events"
                keystroke "r" using {command down, shift down}
            end tell
            '''
            subprocess.run(["osascript", "-e", cmd_shift_r_script],
                         check=False, capture_output=True)

            # Also try Alt+Command+R as a backup
            alt_cmd_r_script = '''
            tell application "System Events"
                keystroke "r" using {command down, option down}
            end tell
            '''
            subprocess.run(["osascript", "-e", alt_cmd_r_script],
                          check=False, capture_output=True)

            logger.info("AppleScript keystrokes sent successfully")
            return True

        except Exception as e:
            logger.error("Error sending keystrokes via AppleScript: %s", str(e))
            return False

    def show_notification(self, title, message):
        """Show a notification popup to the user"""
        try:
            # Only use native notifications - no QMessageBox popup
            logger.info("Displaying notification: %s - %s", title, message)
            self._send_native_notification(title, message)
            logger.info("Notification shown successfully: %s - %s", title, message)
        except Exception as e:
            logger.error("Error showing notification: %s", str(e))

    def _send_native_notification(self, title, message):
        """Send a native OS notification as backup"""
        try:
            if sys.platform == 'darwin':  # macOS
                # Use simple Python subprocess to send notification on macOS
                import subprocess
                subprocess.run([
                    "osascript",
                    "-e",
                    f'display notification "{message}" with title "{title}"'
                ], check=False, capture_output=True)
                logger.info("Native macOS notification sent")
            elif sys.platform == 'win32':  # Windows
                # For Windows, we could implement a Windows notification here
                logger.info("Native Windows notification not implemented yet")
            else:
                logger.info("Native notification not implemented for this OS")
        except Exception as e:
            logger.error("Error sending native notification: %s", str(e))

def main():
    logger.info("Starting Zoom Recording Prompt application")
    app = QApplication(sys.argv)
    window = ZoomRecordingPrompt()
    window.hide()  # Hide the window after initialization
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
