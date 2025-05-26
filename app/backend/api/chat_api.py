from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel 
from typing import Literal
from app.backend.services.firestore_session_service import load_or_create_session, save_session
from app.backend.core.llm_parser import detect_llm_flags, update_intent_state
from app.backend.core.llm_client import prepare_llm_payload, generate_llm_response, format_flights_beautifully
from app.backend.core.flight_engine import handle_search


# ─────────────────────────────────────────────
# FASTAPI APPLICATION INITIALIZATION
router = APIRouter()

# ─────────────────────────────────────────────
# DATA MODELS :
class ChatRequest(BaseModel):
    sessionId : str
    query : str
    currency : Literal["EUR", "USD", "MAD"] = "EUR"

class ChatResponse(BaseModel):
    sessionId : str
    answer : str

# ─────────────────────────────────────────────
# DEFINITION OF THE CHAT ROUTE WITTH ALL ORCHESTRATION :
@router.post("/chat", response_model=ChatResponse, status_code=200)
def chat(request : ChatRequest):
    """
    Main endpoint for chat interaction. 
    Handles session management, LLM generation, and flight search orchestration.
    """

    # Unpack incoming data
    session_id = request.sessionId
    user_query = request.query
    currency = request.currency
    
    # Get or Create Session 
    session = load_or_create_session(session_id)

    # Append User's message to conversation history
    session["conversation_history"].append({"role":"user", "content": user_query})

    # Build LLM messages (injects system prompt + intent_state)
    messages = prepare_llm_payload(session["conversation_history"], mode="chat")

    # Get LLM response
    llm_answer = generate_llm_response(messages)

    # Append llm's message to conversation history
    session["conversation_history"].append({"role":"assistant", "content": llm_answer})

    # Analyze llm's response for flags and act accordingly.
    cleaned_llm_answer, flag = detect_llm_flags(llm_answer)
                                      
    # Catch `[Do_Search]` flag from LLM indicating the user confirmed search
    if flag == "Do_Search":

        # Update intent state
        session["intent_state"] = update_intent_state(session["intent_state"], session["conversation_history"])

        #  Perform flight search 
        search_results = handle_search(session["intent_state"], currency)

        # Format raw search results using LLM into beautiful Markdown for chat display
        search_results = format_flights_beautifully(search_results)

        # Combine cleaned LLM response with the formatted search results
        full_answer = f"{cleaned_llm_answer}\n\n{search_results}"

        # Append only the formatted flight results to the conversation history
        session["conversation_history"].append({"role": "assistant", "content": search_results})

        # Persist updated session
        save_session(session)

        # Return full reply including both conversation and flight results
        return ChatResponse(sessionId=session_id, answer=full_answer)


    # Save the session
    save_session(session)

    # Return the cleaned LLM answer
    return ChatResponse(sessionId=session_id, answer=cleaned_llm_answer)





































