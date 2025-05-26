from datetime import datetime
import calendar
import re


STATIC_CONVERSION_RATES = {
    "MAD": {"EUR": 0.09, "USD": 0.10},
    "EUR": {"MAD": 11.0, "USD": 1.1},
    "USD": {"MAD": 10.0, "EUR": 0.91},
}

def simple_currency_convert(amount, from_currency, to_currency):
    if from_currency == to_currency or to_currency is None:
        return amount  # No conversion needed
    try:
        rate = STATIC_CONVERSION_RATES[from_currency][to_currency]
        return round(amount * rate)
    except KeyError:
        print(f"⚠️ No rate for {from_currency} → {to_currency}. Returning original amount.")
        return amount
    

def format_datetime_compact(datetime_str):
    try:
        dt = datetime.strptime(datetime_str, "%I:%M %p on %a, %b %d")
        now = datetime.now()
        dt = dt.replace(year=now.year)
        if dt < now:
            dt = dt.replace(year=now.year + 1)
        return dt.strftime("%d/%m/%Y | %I:%M %p")
    except:
        return datetime_str


def parse_and_filter_flights(result, max_stops=1, max_price=None, currency="EUR", max_results=5):
    if not result.flights:
        return []

    flights = []
    seen = set()

    for flight in result.flights:
        try:
            raw_flight_price = flight.price.replace('\xa0', '')
            match = re.search(r"\d+", raw_flight_price)
            if not match:
                continue

            flight_price = int(match.group())
            flight_price_currency = re.sub(r"\d+", "", raw_flight_price).strip() or "EUR"
            converted_price = simple_currency_convert(flight_price, flight_price_currency, currency)

            if max_stops is not None and flight.stops > max_stops:
                continue
            if max_price is not None and converted_price > max_price:
                continue

            flight_key = (flight.name, flight.departure, flight_price)
            if flight_key in seen:
                continue
            seen.add(flight_key)

            flights.append({
                "airline": flight.name,
                "departure_raw": flight.departure,
                "arrival_raw": flight.arrival,
                "duration": flight.duration,
                "stops": flight.stops,
                "price": converted_price,
                "currency": currency,
                "is_best": flight.is_best,
            })

        except Exception:
            continue

    flights.sort(key=lambda f: (f["stops"], f["price"]))
    top_flights = flights[:max_results]

    for f in top_flights:
        f["departure"] = format_datetime_compact(f.pop("departure_raw"))
        f["arrival"] = format_datetime_compact(f.pop("arrival_raw"))

    return top_flights


def format_one_way_results_for_llm(flights_data):
    if not flights_data:
        return "No flights found for the requested criteria."

    lines = []

    for idx, flight in enumerate(flights_data, start=1):

        lines.append(
            f"{idx}. ✈️  {flight['airline']} | {flight['departure']} → {flight['arrival']}\n"
            f"    Duration: {flight['duration']} | Stops: {flight['stops']}\n"
            f"    Price: {flight['price']} {flight['currency']}"
        )

    return "\n\n".join(lines)


def format_fixed_round_trip_results_for_llm(round_trips):
    if not round_trips:
        return "No round-trip flights found for the requested criteria."

    lines = []

    for idx, trip in enumerate(round_trips, start=1):
        lines.append(
            f"{idx}. ✈️  Outbound: {trip['airline_out']} | {trip['departure_out']} → {trip['arrival_out']}\n"
            f"    Duration: {trip['duration_out']} | Stops: {trip['stops_out']} | Price: {trip['price_out']} {trip['currency']}\n"
            f"    ↩️  Return:   {trip['airline_return']} | {trip['departure_return']} → {trip['arrival_return']}\n"
            f"    Duration: {trip['duration_return']} | Stops: {trip['stops_return']} | Price: {trip['price_return']} {trip['currency']}\n"
            f"    💰 Total: {trip['total_price']} {trip['currency']}"
        )

        if trip.get("same_airline"):
            lines[-1] += "\n    🔁 Same airline for both segments"

    return "\n\n".join(lines)


def format_cheapest_round_trip_results_for_llm(round_trips):
    if not round_trips:
        return "No round-trip flights found for the requested criteria."

    lines = []

    for idx, trip in enumerate(round_trips, start=1):
        # Extract only the time part from arrival strings
        arrival_out_time = trip['arrival_out'].split("|")[-1].strip()
        arrival_return_time = trip['arrival_return'].split("|")[-1].strip()

        lines.append(
            f"{idx}. ✈️  Outbound: {trip['airline_out']} | {trip['departure_out'].strftime('%Y-%m-%d')} | {trip['departure_out'].strftime('%I:%M %p')} → {arrival_out_time}\n"
            f"    Duration: {trip['duration_out']} | Stops: {trip['stops_out']} | Price: {trip['price_out']} {trip['currency']}\n"
            f"    ↩️  Return:   {trip['airline_return']} | {trip['departure_return'].strftime('%Y-%m-%d')} | {trip['departure_return'].strftime('%I:%M %p')} → {arrival_return_time}\n"
            f"    Duration: {trip['duration_return']} | Stops: {trip['stops_return']} | Price: {trip['price_return']} {trip['currency']}\n"
            f"    🕒 Stay length: {trip['length_stay']} days\n"
            f"    💰 Total: {trip['total_price']} {trip['currency']}"
        )

        if trip.get("same_airline"):
            lines[-1] += "\n    🔁 Same airline for both segments"

    return "\n\n".join(lines)



def format_monthly_price_calendar(flights_data):
    if not flights_data:
        return "No flight prices available."

    lines = ["🗓️  Price Overview:\n"]

    for f in flights_data:
        date_str = f["departure"]
        airline = f["airline"]
        price = f["price"]
        currency = f["currency"]
        lines.append(f"{date_str} — {airline} — {price} {currency}")

    return "\n".join(lines)


