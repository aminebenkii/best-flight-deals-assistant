import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from app.backend.utils.utils import load_json, save_json

# ─────────────────────────────────────────────
# PATH CONFIGURATION
PROJECT_ROOT_DIR = Path(__file__).resolve().parents[3]
SESSIONS_STORAGE_PATH = PROJECT_ROOT_DIR / "storage" / "sessions"

# Ensure the sessions directory exists
os.makedirs(SESSIONS_STORAGE_PATH, exist_ok=True)


def load_or_create_session(session_id):
    """
    Retrieves an existing session by ID or creates a new one if it doesn't exist.
    """
    session_file_path = os.path.join(SESSIONS_STORAGE_PATH, f"{session_id}.json")

    if os.path.exists(session_file_path):
        return load_json(session_file_path)

    session_data = {
        "creation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "session_id": session_id,
        "conversation_history": [],
        "intent_state": {
            "origin": None,
            "destination": None,
            "departure_date": None,     
            "return_date": None,        
            "stay_length": None,        
            "max_stops": 1,
            "max_price": None,
        }
    }
    return session_data



def save_session(session_data):
    """
    Saves session data to a JSON file using the session ID as the filename.
    """

    session_id = session_data.get("session_id")
    if not session_id:
        raise ValueError("Session data must include a 'session_id' key.")

    session_file_path = os.path.join(SESSIONS_STORAGE_PATH, f"{session_id}.json")
    save_json(session_file_path, session_data)

