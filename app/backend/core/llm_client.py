import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from app.backend.core.config import LLM_COLLECTION_PROMPT, LLM_EXTRACTION_PROMPT, LLM_MODEL, FORMAT_PROMPT
from app.backend.utils.utils import get_config_value

# ─────────────────────────────────────────────
# PATH CONFIGURATION
PROJECT_ROOT_DIR = Path(__file__).resolve().parents[2]
DOTENV_PATH = PROJECT_ROOT_DIR / ".env"

# ─────────────────────────────────────────────
# CLIENT INITIALIZATION
load_dotenv(DOTENV_PATH)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ─────────────────────────────────────────────
# FUNCTION DEFINITIONS

def prepare_llm_payload(conversation, mode):
    """ Constructs the message payload for the LLM API."""

    if mode == "chat":
        messages = [{"role": "system", "content": f"{LLM_COLLECTION_PROMPT}"}] + conversation
        return messages
    
    elif mode == "extraction":
        messages = [{"role": "system", "content": f"{LLM_EXTRACTION_PROMPT}"}] + conversation
        return messages


def generate_llm_response(messages):
    """ Calls the LLM API and returns the generated response."""

    llm_model = LLM_MODEL or "gpt-4o-mini"

    try:
        response = openai_client.chat.completions.create(
            model=llm_model,
            messages=messages,
            temperature=0.3,
            max_tokens=500
        )

        print("number of cached tokens:", response.usage.prompt_tokens_details.cached_tokens)
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error occurred while generating response: {str(e)}"


def format_flights_beautifully(text):
    """ Calls the LLM API and returns the generated response."""

    llm_model = LLM_MODEL or "gpt-4o-mini"

    messages = [{"role": "system", "content": f"{FORMAT_PROMPT}"}] + [{"role": "user", "content": f"{text}"}]

    try:
        response = openai_client.chat.completions.create(
            model=llm_model,
            messages=messages,
            temperature=1,
            max_tokens=1000
        )

        print("number of cached tokens:", response.usage.prompt_tokens_details.cached_tokens)
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error occurred while generating response: {str(e)}"
