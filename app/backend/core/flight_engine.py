from app.backend.utils.utils import get_config_value
from app.backend.flights.search_functions import search_one_way_fixed, search_one_way_cheapest
from app.backend.flights.search_functions import  search_round_trip_fixed, search_round_trip_cheapest
import re


# ─────────────────────────────────────────────
# FUNCTION DEFINITIONS

def handle_search(intent_state, currency):
    """
    Handle the search based on the intent state.
    """

    valid_intent, error = validate_intent(intent_state)
    if not valid_intent:
        return error

    search_type = infer_search_type(intent_state)

    if search_type == "one_way_fixed":
        args = convert_intent_to_search_params(intent_state, search_type, currency)
        return search_one_way_fixed(**args)

    elif search_type == "one_way_cheapest":
        args = convert_intent_to_search_params(intent_state, search_type, currency)
        return search_one_way_cheapest(**args)
    
    elif search_type == "round_trip_fixed":
        args = convert_intent_to_search_params(intent_state, search_type, currency)
        return search_round_trip_fixed(**args)  
    
    elif search_type == "round_trip_cheapest":
        args = convert_intent_to_search_params(intent_state, search_type, currency)
        return search_round_trip_cheapest(**args)
    

  

def validate_intent(intent_state):
    """
    Validate the intent state before triggering a flight search.
    """

    # Extract Fields
    origin = intent_state.get("origin")
    destination = intent_state.get("destination")
    departure_date = intent_state.get("departure_date")
    return_date = intent_state.get("return_date")
    stay_length = intent_state.get("stay_length")
    max_stops = intent_state.get("max_stops")

    # 1. Basic required fields
    if not origin:
        return False, "Missing 'origin'."
    if not destination:
        return False, "Missing 'destination'."
    if not departure_date:
        return False, "Missing 'departure_date'."

    # 2. Validate departure_date format
    valid_dep = (
        re.fullmatch(r"\d{4}-\d{2}-\d{2}", departure_date) or
        re.fullmatch(r"earliest:\d{4}-\d{2}-\d{2}", departure_date) or
        re.fullmatch(r"earliest:\d{4}-\d{2}-\d{2},latest:\d{4}-\d{2}-\d{2}", departure_date)
    )
    if not valid_dep:
        return False, "Invalid 'departure_date' format."

    # 3. Validate return_date if present
    if return_date:
        valid_ret = (
            re.fullmatch(r"\d{4}-\d{2}-\d{2}", return_date) or
            re.fullmatch(r"latest:\d{4}-\d{2}-\d{2}", return_date)
        )
        if not valid_ret:
            return False, "Invalid 'return_date' format."

    # 4. If latest return is used, stay_length must be present
    if return_date and return_date.startswith("latest:") and not stay_length:
        return False, "Flexible round-trip requires 'stay_length'."

    # 5. Optional: validate max_stops
    if max_stops is not None:
        try:
            int(max_stops)
        except ValueError:
            return False, "'max_stops' must be a number."

    return True, ""


def infer_search_type(intent_state):
    """
    Infer the appropriate search type based on the structure of the intent_state fields.
    Returns one of:
    - one_way_fixed
    - one_way_cheapest
    - round_trip_fixed
    - round_trip_cheapest
    """

    departure_date = intent_state.get("departure_date")
    return_date = intent_state.get("return_date")
    stay_length = intent_state.get("stay_length")

    if not departure_date:
        return None

    # One-way fixed: exact date, no return, no stay length
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", departure_date) and not return_date and not stay_length:
        return "one_way_fixed"

    # One-way cheapest: departure_date is a range like 'earliest:...,latest:...'
    if "earliest:" in departure_date and "latest:" in departure_date and not return_date and not stay_length:
        return "one_way_cheapest"

    # Round-trip fixed: both are exact dates
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", departure_date) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", return_date or ""):
        return "round_trip_fixed"

    # Round-trip cheapest: 
    if ("earliest:" in departure_date) and (return_date is None or return_date.startswith("latest:")) and stay_length:
        return "round_trip_cheapest"

    return None


def convert_intent_to_search_params(intent_state, search_type, currency):
    """
    Convert the intent_state into actual parameters for the selected search function.
    """

    # Extract shared fields
    origin = intent_state.get("origin")
    destination = intent_state.get("destination")
    departure_date = intent_state.get("departure_date")
    return_date = intent_state.get("return_date")
    stay_length = intent_state.get("stay_length")
    max_stops = int(intent_state.get("max_stops", 1))
    max_price = intent_state.get("max_price")

    # Define shared/general args
    general_args = {
        "origin": origin,
        "destination": destination,
        "max_stops": max_stops,
        "currency": currency,
    }


    # Parse price like "300", "300EUR", "EUR300", "300 EUR", "EUR 300"
    if isinstance(max_price, str):
        match = re.search(r"\d+", max_price)
        if match:
            max_price = int(match.group())
        else:
            max_price = None

    # Only include max_price for search types that support it
    if max_price is not None and search_type in ["one_way_fixed", "round_trip_fixed"]:
        general_args["max_price"] = max_price



    # 1️⃣ One-way fixed
    if search_type == "one_way_fixed":
        return {
            **general_args,
            "departure_date": departure_date
        }

    # 2️⃣ One-way cheapest
    if search_type == "one_way_cheapest":
        start, end = departure_date.replace("earliest:", "").split(",latest:")
        return {
            **general_args,
            "start_date": start,
            "end_date": end
        }

    # 3️⃣ Round-trip fixed
    if search_type == "round_trip_fixed":
        return {
            **general_args,
            "departure_date": departure_date,
            "return_date": return_date
        }

    # 4️⃣ Round-trip cheapest
    if search_type == "round_trip_cheapest":
        min_stay, max_stay = [int(x) for x in stay_length.split("-")] if "-" in stay_length else [int(stay_length)] * 2

        if "," in departure_date:
            start_departure_date, end_departure_date = departure_date.replace("earliest:", "").split(",latest:")
            return {
                **general_args,
                "start_departure_date": start_departure_date,
                "end_departure_date": end_departure_date,
                "latest_return_date": None,
                "min_stay_days": min_stay,
                "max_stay_days": max_stay
            }

        if return_date and return_date.startswith("latest:"):
            start_departure_date = departure_date.replace("earliest:", "")
            latest_return_date = return_date.replace("latest:", "")
            return {
                **general_args,
                "start_departure_date": start_departure_date,
                "end_departure_date": None,
                "latest_return_date": latest_return_date,
                "min_stay_days": min_stay,
                "max_stay_days": max_stay
            }

    return {}