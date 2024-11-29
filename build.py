#!/usr/bin/env python3

import subprocess
import logging
import os
import sys
import shutil

# Setup logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("build_white_rabbit.log"),
                        logging.StreamHandler(sys.stdout)
                    ])

logger = logging.getLogger(__name__)

def run_command(command, log_message):
    """Run a shell command and log the output."""
    logger.info(log_message)
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        logger.info(f"Command output: {result.stdout}")
        logger.info("Command executed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing command: {e.stderr}")
        sys.exit(1)

def clean_build_files():
    """Delete build directories and spec file."""
    directories_to_remove = ['dist', 'build']
    files_to_remove = ['WhiteRabbit.spec']

    for directory in directories_to_remove:
        if os.path.exists(directory):
            logger.info(f"Removing directory: {directory}")
            shutil.rmtree(directory)
    
    for file in files_to_remove:
        if os.path.exists(file):
            logger.info(f"Removing file: {file}")
            os.remove(file)

def get_desktop_path():
    """Get the path to the user's Desktop folder."""
    return os.path.join(os.path.expanduser("~"), "Desktop")

def create_play_audio_script():
    """Create or overwrite the play_audio.sh script on the user's Desktop."""
    desktop_path = get_desktop_path()
    play_audio_script_path = os.path.join(desktop_path, 'play_audio.sh')

    # Set the file_path directly to the Desktop
    file_path = os.path.join(desktop_path, 'audio_path.txt')

    logger.info(f"Creating or overwriting play_audio.sh on the Desktop: {play_audio_script_path}")
    try:
        with open(play_audio_script_path, 'w') as f:
            # Write the shell script to play audio
            f.write(f"""#!/bin/bash

# Check if an audio path argument was provided
if [ "$#" -ne 1 ]; then
    echo "Usage: ./play_audio.sh <audio_path>"
    exit 1
fi

# Get the audio file path from the argument
audio_path="$1"

# Write the audio file path to audio_path.txt
echo "$audio_path" > {file_path}

# Check if WhiteRabbit is already running
if pgrep -x "WhiteRabbit" > /dev/null; then
    echo "Stopping existing WhiteRabbit player..."
    # Kill the existing WhiteRabbit process
    pkill -x "WhiteRabbit"
    sleep 1  # Give it a moment to stop
fi

# Run the WhiteRabbit player with the audio path argument
open -a /Applications/WhiteRabbit.app --args "$audio_path"
""")
        # Make the script executable
        os.chmod(play_audio_script_path, 0o755)
        logger.info("play_audio.sh created and made executable.")
    except Exception as e:
        logger.error(f"Error creating play_audio.sh: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Clean up previous builds
    clean_build_files()

    # Define the build commands
    build_commands = [
        {
            "command": ["pyinstaller", "--name", "WhiteRabbit", "--icon", "rabbit.png", "--windowed", "--add-data=audio_path.txt:.", "white_rabbit_player.py"],
            "log_message": "Running PyInstaller to build the application..."
        },
        {
            "command": ["mkdir", "-p", "dist/dmg"],
            "log_message": "Creating directory for DMG file..."
        },
        {
            "command": ["cp", "-r", "dist/WhiteRabbit.app", "dist/dmg"],
            "log_message": "Copying .app file to the DMG directory..."
        },
        {
            "command": [
                "create-dmg",
                "--volname", "WhiteRabbit",
                "--volicon", "rabbit.png",
                "--window-pos", "200", "120",
                "--window-size", "600", "300",
                "--icon-size", "100",
                "--icon", "WhiteRabbit.app", "175", "120",
                "--hide-extension", "WhiteRabbit.app",
                "--app-drop-link", "425", "120",
                "dist/WhiteRabbit.dmg", "dist/dmg/"
            ],
            "log_message": "Creating DMG file..."
        }
    ]

    # Execute each command with logging
    for cmd in build_commands:
        run_command(cmd["command"], cmd["log_message"])

    # After building, create the audio_path.txt and play_audio.sh files on the Desktop
    create_play_audio_script()

    logger.info("Build process completed successfully.")
