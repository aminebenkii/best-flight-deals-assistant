from fast_flights import FlightData, Passengers, get_flights
from app.backend.flights.formatters import parse_and_filter_flights, format_one_way_results_for_llm
from app.backend.flights.formatters import format_cheapest_round_trip_results_for_llm
from app.backend.flights.formatters import format_fixed_round_trip_results_for_llm, format_monthly_price_calendar
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta


def get_one_way_fixed_list(origin, destination, departure_date, max_stops=1, max_price=None, currency="EUR", max_results=5):
    """
    Returns raw parsed one-way flights, not formatted for LLM.
    """
    try:
        result = get_flights(
            flight_data=[FlightData(date=departure_date, from_airport=origin, to_airport=destination, max_stops=max_stops)],
            trip="one-way",
            seat="economy",
            passengers=Passengers(adults=1),
            fetch_mode="fallback"
        )

        return parse_and_filter_flights(
            result,
            max_results=max_results,
            max_stops=max_stops,
            max_price=max_price,
            currency=currency
        )

    except Exception as e:
        print(f"❌ Error fetching one-way flights: {e}")
        return []


def search_one_way_fixed(*args, **kwargs):
    return format_one_way_results_for_llm(
        get_one_way_fixed_list(*args, **kwargs)
    )


def search_round_trip_fixed(origin, destination, departure_date, return_date, max_stops=1, max_price=None, currency="EUR", max_results=5):
    
    outbound_flights = get_one_way_fixed_list(origin, destination, departure_date, max_stops, None, currency, max_results)
    return_flights  = get_one_way_fixed_list(destination, origin, return_date, max_stops, None, currency, max_results)

    round_trips = []

    for out in outbound_flights:
        for ret in return_flights:
            price_out = out["price"]
            price_ret = ret["price"]
            total_price = price_out + price_ret

            if max_price and total_price > max_price:
                continue

            round_trips.append({
                "airline_out": out["airline"],
                "airline_return": ret["airline"],
                "departure_out": out["departure"],
                "arrival_out": out["arrival"],
                "departure_return": ret["departure"],
                "arrival_return": ret["arrival"],
                "duration_out": out["duration"],
                "duration_return": ret["duration"],
                "stops_out": out["stops"],
                "stops_return": ret["stops"],
                "price_out": price_out,
                "price_return": price_ret,
                "total_price": total_price,
                "currency": currency,
                "same_airline": out["airline"] == ret["airline"]
            })

    # Smart sort:
    # 1. Prioritize direct flights (both legs)
    # 2. Among those, prefer same airline
    # 3. Then sort by total price
    round_trips.sort(key=lambda x: (
    x["stops_out"] > 0 or x["stops_return"] > 0,    # 0 if both legs are direct
    x["airline_out"] != x["airline_return"],        # 0 if same airline
    x["total_price"]                                # lowest price wins
    ))

    # Return formatted string instead of raw list
    return format_fixed_round_trip_results_for_llm(round_trips[:max_results])


def search_one_way_cheapest(origin, destination, start_date, end_date, max_stops=1, currency="EUR", max_results=5):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    dates = [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((end - start).days + 1)]
    all_flights = []

    def fetch(date):
        try:
            return get_one_way_fixed_list(
                origin=origin,
                destination=destination,
                departure_date=date,
                max_stops=max_stops,
                currency=currency,
                max_results=1
            )
        except Exception as e:
            print(f"⚠️ Error fetching for {date}: {e}")
            return []

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(fetch, date) for date in dates]
        for future in as_completed(futures):
            all_flights.extend(future.result())

    all_flights.sort(key=lambda x: x["price"])
    return format_one_way_results_for_llm(all_flights[:max_results])


def search_round_trip_cheapest(origin, destination, start_departure_date, end_departure_date, latest_return_date, min_stay_days, max_stay_days, max_stops=1, currency="EUR", max_results=5):

   # Parse provided dates
    earliest_departure = datetime.strptime(start_departure_date, "%Y-%m-%d")

    # Scenario A — user provides start and end departure dates
    if start_departure_date and end_departure_date:

        latest_departure = datetime.strptime(end_departure_date, "%Y-%m-%d")
        earliest_return = earliest_departure + timedelta(days=min_stay_days)
        latest_return = latest_departure + timedelta(days=max_stay_days)

    # Scenario B — user provides start departure + latest return only
    elif start_departure_date and latest_return_date:
        
        latest_return = datetime.strptime(latest_return_date, "%Y-%m-%d")
        latest_departure = latest_return - timedelta(days=max_stay_days)
        earliest_return = earliest_departure + timedelta(days=min_stay_days)

    else:
        raise ValueError("You must provide either (start_departure_date + end_departure_date) or (start_departure_date + latest_return_date).")


    def daterange(start, end):
        num_days = (end - start).days + 1
        return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(num_days)]
    

    departure_dates = daterange(earliest_departure, latest_departure)
    return_dates = daterange(earliest_return, latest_return)


    all_outbound_flights_cheapest = []
    all_return_flights_cheapest = []

    def fetch(date, orig, dest):
        try:
            return get_one_way_fixed_list(
                origin=orig,
                destination=dest,
                departure_date=date,
                max_stops=max_stops,
                currency=currency,
                max_results=1
            )
        except Exception as e:
            print(f"⚠️ Error fetching for {date}: {e}")
            return []

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(fetch, date, origin, destination) for date in departure_dates]
        for future in as_completed(futures):
            all_outbound_flights_cheapest.extend(future.result())

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(fetch, date, destination, origin) for date in return_dates]
        for future in as_completed(futures):
            all_return_flights_cheapest.extend(future.result())


    for flight in all_outbound_flights_cheapest : 
        flight["departure"] = datetime.strptime(flight["departure"].strip(), "%d/%m/%Y | %I:%M %p")

    for flight in all_return_flights_cheapest : 
        flight["departure"] = datetime.strptime(flight["departure"].strip(), "%d/%m/%Y | %I:%M %p")

    all_outbound_flights_cheapest.sort(key=lambda x : x["departure"])
    all_return_flights_cheapest.sort(key=lambda x : x["departure"])

    
    possible_round_trips = []

    for out in all_outbound_flights_cheapest:
        for ret in all_return_flights_cheapest:

            stay_length = ret["departure"] - out["departure"]
            stay_length = stay_length.days

            if ( stay_length < min_stay_days or stay_length > max_stay_days):
                continue

            price_out = out["price"]
            price_ret = ret["price"]

            total_price = price_out + price_ret

            possible_round_trips.append({
                "airline_out": out["airline"],
                "length_stay": stay_length,
                "airline_return": ret["airline"],
                "departure_out": out["departure"],
                "arrival_out": out["arrival"],
                "departure_return": ret["departure"],
                "arrival_return": ret["arrival"],
                "duration_out": out["duration"],
                "duration_return": ret["duration"],
                "stops_out": out["stops"],
                "stops_return": ret["stops"],
                "price_out": price_out,
                "price_return": price_ret,
                "total_price": total_price,
                "currency": currency,
                "same_airline": out["airline"] == ret["airline"]
            })


    possible_round_trips.sort(key=lambda x: x["total_price"])

    return format_cheapest_round_trip_results_for_llm(possible_round_trips[:max_results])


def search_range_price_list(origin, destination, start_date, end_date, max_stops=1, currency="EUR"):

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    dates = [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((end - start).days + 1)]
    all_flights = []

    def fetch(date):
        try:
            return get_one_way_fixed_list(
                origin=origin,
                destination=destination,
                departure_date=date,
                max_stops=max_stops,
                currency=currency,
                max_results=1
            )
        except Exception as e:
            print(f"⚠️ Error fetching for {date}: {e}")
            return []

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(fetch, date) for date in dates]
        for future in as_completed(futures):
            all_flights.extend(future.result())

    all_flights.sort(key=lambda x: x["departure"])
    return format_monthly_price_calendar(all_flights)


