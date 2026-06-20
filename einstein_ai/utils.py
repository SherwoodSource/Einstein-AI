import logging
import os
import sys
import subprocess
import pkg_resources

def setup_logger(name, log_file="einstein_ai.log", level=logging.INFO):
    """Function to setup as many loggers as you want"""
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s'))

    logger = logging.getLogger(name)
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
        # This is a simple implementation. In a real-world scenario,
        # we'd compare versions more robustly.
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "-r", req_file])
        logger.info("Dependencies are up to date.")
    except Exception as e:
        logger.error(f"Failed to update dependencies: {e}")

def get_data_dir():
    """Returns the path to the data directory"""
    return os.path.join(os.path.dirname(__file__), "data")

def get_index_dir():
    """Returns the path to the faiss_index directory"""
    return os.path.join(os.path.dirname(__file__), "faiss_index")
