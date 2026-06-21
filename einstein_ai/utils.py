import logging
import os
import sys
import subprocess
from datetime import datetime
from urllib.parse import urlparse

# Set level to INFO for production-like behavior
def setup_logger(name, log_file="einstein_ai.log", level=logging.INFO):
    """Function to setup as many loggers as you want"""
    # Remove existing handlers to avoid duplicates
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        logger.handlers.clear()

    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s'))

    logger.setLevel(level)
    logger.addHandler(handler)

    # Also log to console for development visibility
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(console_handler)

    return logger

logger = setup_logger("EinsteinAI")

def sync_dependencies():
    """Checks requirements.txt and updates dependencies if needed"""
    req_file = "requirements.txt"
    if not os.path.exists(req_file):
        logger.warning("requirements.txt not found. Skipping auto-update.")
        return

    logger.info("Checking for dependency updates...")
    try:
        # Redirect stdout/stderr to devnull to keep the launch clean
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-U", "-r", req_file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        logger.info("Dependencies are up to date.")
    except Exception as e:
        logger.error(f"Failed to update dependencies: {e}")

def get_data_dir():
    """Returns the path to the data directory"""
    return os.path.join(os.path.dirname(__file__), "data")

def get_index_dir():
    """Returns the path to the faiss_index directory"""
    return os.path.join(os.path.dirname(__file__), "faiss_index")

def get_history_dir():
    """Returns the path to the history directory"""
    history_dir = os.path.join(os.path.dirname(__file__), "history")
    if not os.path.exists(history_dir):
        os.makedirs(history_dir)
    return history_dir

def log_interaction(user_input, bot_response):
    """Logs a single interaction to the current session's history file"""
    history_dir = get_history_dir()
    # One file per day to keep things organized
    filename = f"chat_{datetime.now().strftime('%Y-%m-%d')}.txt"
    filepath = os.path.join(history_dir, filename)

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with open(filepath, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] USER: {user_input}\n")
        f.write(f"[{timestamp}] EINSTEIN: {bot_response}\n\n")

def add_online_source(url, triggers=""):
    """Adds a new online source to SOURCES.env with trigger words"""
    env_file = "SOURCES.env"

    # Extract name from URL
    parsed_url = urlparse(url)
    name = os.path.basename(parsed_url.path)
    if not name or name in ['', '/']:
        name = "WebSource_" + datetime.now().strftime('%H%M%S')

    # Strip extension for the name
    name = os.path.splitext(name)[0].upper().replace("-", "_").replace(".", "_")

    line = f"{name}={url}|{triggers}\n"

    # Check if SOURCES.env exists, if not create with header
    if not os.path.exists(env_file):
        with open(env_file, "w") as f:
            f.write("# Einstein AI Sources and Trigger Words\n")
            f.write("# Format: SOURCE_NAME=URL|TRIGGER1,TRIGGER2,...\n\n")

    # Append the new source
    with open(env_file, "a") as f:
        f.write(line)

    logger.info(f"Added new source '{name}' to {env_file}")
    return name
