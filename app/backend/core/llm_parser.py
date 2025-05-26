from app.backend.core.llm_client import prepare_llm_payload, generate_llm_response

def detect_llm_flags(llm_response):
    """
    Extracts [extracted] or [Do_Search] from the final line.
    """
    try:
        lines = llm_response.strip().splitlines()
        if not lines:
            return llm_response, None

        last_line = lines[-1].strip()

        if last_line.startswith("[Do_Search]"):
                return "\n".join(lines[:-1]).strip(), "Do_Search"
        
        return llm_response, None

    except Exception as e:
        print(f"Error in detect_llm_flags: {e}")
        return llm_response, None



def update_intent_state(intent_state, conversation):
    """
    Update the intent_state dictionary with key=value strings from the LLM payload.
    """

    messages = prepare_llm_payload(conversation, mode="extraction")
    llm_answer = generate_llm_response(messages)
    print("LLM Extraction Answer:", llm_answer)

    llm_answer = llm_answer.replace("[extracted]", "").strip()
    payload = llm_answer.split()

    ALLOWED_KEYS = {
        "origin", "destination", "departure_date",
        "return_date", "stay_length", "max_stops", "max_price"
    }

    for item in payload:
        try:
            key, value = item.strip().split("=", 1)
            if key in ALLOWED_KEYS:
                intent_state[key] = value
        except ValueError:
            print(f"⚠️ Skipping malformed payload item: '{item}'")

    return intent_state



