import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import json
from google.cloud import firestore

# ─────────────────────────────────────────────
# PATH CONFIGURATION
PROJECT_ROOT_DIR =  Path(__file__).resolve().parents[3]
JSON_AUTH_PATH = PROJECT_ROOT_DIR / "app" / "backend" / "credentials" /  "flight-deals-chatbot-5ffc48721eef.json"

# AUTHENTICATION SETUP (Set path to your downloaded JSON key)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(JSON_AUTH_PATH)

# ─────────────────────────────────────────────
# FIRESTORE CONFIGURATION
db = firestore.Client()
SESSIONS_COLLECTION = "sessions"

def load_or_create_session(session_id: str) -> Dict[str, Any]:
    """
    Retrieves an existing session from Firestore or creates a new one.
    """
    doc_ref = db.collection(SESSIONS_COLLECTION).document(session_id)
    doc = doc_ref.get()

    if doc.exists:
        return doc.to_dict()

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
    doc_ref.set(session_data)
    return session_data


def save_session(session_data: Dict[str, Any]):
    """
    Saves session data to Firestore using the session ID as the document ID.
    """
    session_id = session_data.get("session_id")
    if not session_id:
        raise ValueError("Session data must include a 'session_id' key.")

    doc_ref = db.collection(SESSIONS_COLLECTION).document(session_id)
    doc_ref.set(session_data)