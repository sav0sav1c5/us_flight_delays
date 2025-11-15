import time
from pymongo import InsertOne
from collections import defaultdict
from tqdm import tqdm

def cache_airports(database):
    """
    Function for caching airport data.
    """

    airports_cache = {}

    for airport in database['airports'].find({}):

        iata_code = airport.get('iata_code')

        if iata_code:
            airports_cache[iata_code.upper()] = airport

    return airports_cache

def cache_airport_geolocations(database):
    """
    Function for caching airport geolocation data.
    """
    airport_geolocations_cache = {}

    for geolocation in database['airports_geolocation'].find({}):

        iata_code = geolocation.get('IATA_CODE')

        if iata_code:
            airport_geolocations_cache[iata_code.upper()] = geolocation

    return airport_geolocations_cache

def cache_runways(database):
    """
    Function for caching runways data by airport where they are locatied.
    """

    runways_cache = defaultdict(list)

    for runway in database['runways'].find({}):

        airport_ident = runway.get('airport_ident')

        if airport_ident:
            runways_cache[airport_ident].append(runway)

    return runways_cache

def cache_airport_frequencies(database):
    """
    Function for caching airport frequencies data by airport of which they are part of.
    """

    airport_frequencies_cache = defaultdict(list)

    for airport_frequency in database['airport_frequencies'].find({}):

        airport_ident = airport_frequency.get('airport_ident')

        if airport_ident:
            airport_frequencies_cache[airport_ident.upper()].append(airport_frequency)

    return airport_frequencies_cache

def cache_weather(database):
    """
    Function for caching weather data by airport id and time when it's recorded.
    """

    weather_cache = {}

    for weather in database['weather_meteo_by_airport'].find({}):

        key = (weather.get('airport_id'), str(weather.get('time')))

        weather_cache[key] = {
            "tavg": weather.get('tavg'),
            "tmin": weather.get('tmin'),
            "tmax": weather.get('tmax'),
            "prcp": weather.get('prcp'),
            "snow": weather.get('snow'),
            "wdir": weather.get('wdir'),
            "wspd": weather.get('wspd'),
            "pres": weather.get('pres')
        }

    return weather_cache

def cache_flight_status(database):
    """
    Function for caching flight status data (cancelled/diverted).
    """

    flight_status_cache = {}

    for flight_status in database['cancelled_deverted_2023'].find({}):

        key = (str(flight_status.get('FlightDate')), flight_status.get('Airline'), flight_status.get('Dep_Airport'), flight_status.get('Arr_Airport'))

        flight_status_cache[key] = {
            "cancelled" : flight_status.get('Cancelled', 0),
            "deverted" : flight_status.get('Deverted', 0)
        }

    return flight_status_cache

def create_weather_collection(database, weather_cache, batch_size = 10000):
    """
    Function for creating normalized weather collection.
    """

    collection = database['weather_hybrid_optimized']
    collection.drop()

    documents = []

    for (airport_id, date), weather_data in weather_cache.items():

        document = {
            "airport_id" : airport_id,
            "date" : date,
            "tavg" : weather_data.get('tavg'),
            "tmin" : weather_data.get('tmin'),
            "tmax" : weather_data.get('tmax'),
            "prcp" : weather_data.get('prcp'),
            "snow" : weather_data.get('snow'),
            "wdir" : weather_data.get('wdir'),
            "wspd" : weather_data.get('wspd'),
            "pres" : weather_data.get('pres')
        }
    
        documents.append(InsertOne(document))

        if len(documents) >= batch_size:
            collection.bulk_write(documents, ordered = False)
            documents = []

    if documents:
        collection.bulk_write(documents, ordered = False)

    return collection

def calculate_airport_summary_metrics(runways, airport_frequencies):
    """
    Function for calculating aggregated metrics for a passed airport.
    """
    # Calculate runway metrics
    runway_count = len(runways)
    max_runway_length_ft = max((runway.get('length_ft') or 0) for runway in runways) if runways else 0
    has_lighted_runway = any((runway.get('lighted') == 1) for runway in runways)
    
    # Get unique surfaces
    surfaces = sorted({(runway.get('surface') or "") for runway in runways if runway.get('surface')})
    
    # Calculate frequency metrics
    frequency_count = len(airport_frequencies)
    has_twr = any((frequency.get('type') == 'TWR') for frequency in airport_frequencies)

    return {
        "runway_count" : runway_count,
        "max_runway_length_ft" : max_runway_length_ft,
        "has_lighted_runway" : has_lighted_runway,
        "surfaces" : surfaces,
        "frequency_count" : frequency_count,
        "has_twr" : has_twr,
    }

def create_airport_summary_collection(database, airports_cache, geolocations_cache, runways_cache,
                                      airport_frequencies_cache, batch_size = 10000):
    """
    Function for creating airports_summary collection with aggregated data.
    """

    collection = database['airports_summary_hybrid_optimized']
    collection.drop()

    documents = []

    for iata_code, airport in airports_cache.items():

        geolocation = geolocations_cache.get(iata_code)

        ident = airport.get('ident')
        runways = runways_cache.get(ident, [])
        airport_frequencies = airport_frequencies_cache.get(ident, [])

        metrics = calculate_airport_summary_metrics(runways, airport_frequencies)

        document = {
            "iata" : iata_code,
            "ident" : airport.get('ident'),
            "type" : airport.get('type'),
            "name" : airport.get('name'),
            "elevation_ft" : airport.get('elevation_ft'),
            "municipality" : airport.get('municipality'),
            "country" : geolocation.get('COUNTRY') if geolocation else None,
            "home_link" : airport.get('home_link'),
            "local_code" : airport.get('local_code'),
            "runway_count" : metrics['runway_count'],
            "max_runway_length_ft" : metrics['max_runway_length_ft'],
            "has_lighted_runway" : metrics['has_lighted_runway'],
            "surfaces" : metrics['surfaces'],
            "frequency_count" : metrics['frequency_count'],
            "has_twr" : metrics['has_twr']
        }

        documents.append(InsertOne(document))

        if len(documents) >= batch_size:
            collection.bulk_write(documents, ordered = False)
            documents = []

    if documents:
        collection.bulk_write(documents, ordered = False)
        
    return collection

def build_optimized_flight_document(flight, airports_cache, geolocations_cache, runways_cache,
                                    airport_frequencies_cache, weather_cache, flight_status_cache):
    """
    Function for building flight documents for optimized schema.
    """
    flight_date = str(flight.get('FlightDate'))
    airline = flight.get('Airline')
    dep_iata = flight.get('Dep_Airport')
    arr_iata = flight.get('Arr_Airport')

    flight_status_key = (flight_date, airline, dep_iata, arr_iata)
    flight_status = flight_status_cache.get(flight_status_key, {
        "cancelled" : 0,
        "deverted" : 0
    })

    dep_airport = airports_cache.get(dep_iata) if dep_iata else None
    arr_airport = airports_cache.get(arr_iata) if arr_iata else None

    dep_geo = geolocations_cache.get(dep_iata) if dep_iata else None
    arr_geo = geolocations_cache.get(arr_iata) if arr_iata else None

    dep_weather = weather_cache.get((dep_iata, flight_date))
    arr_weather = weather_cache.get((arr_iata, flight_date))

    dep_ident = dep_airport.get('ident') if dep_airport else dep_iata
    dep_runways = runways_cache.get(dep_ident, [])
    dep_frequencies = airport_frequencies_cache.get(dep_ident, [])

    if dep_airport:
        dep_metrics = calculate_airport_summary_metrics(dep_runways, dep_frequencies) 
    else:
        dep_metrics = {
            "runway_count": 0,
            "max_runway_length_ft": 0,
            "has_lighted_runway": False,
            "surfaces": [],
            "frequency_count": 0,
            "has_twr": False
        }

    document = {
        "flight_id" : f"{airline}_{flight_date}_{dep_iata}_{arr_iata}",
        "flight_date" : flight_date,
        "day_of_week" : flight.get('Day_of_Week'),
        "airline" : airline,
        "tail_number" : flight.get('Tail_Number'),
        "status" : flight_status,
        "departure" : {
            "airport_code" : dep_iata,
            "city" : flight.get('Dep_CityName') or (dep_geo.get('CITY') if dep_geo else None),
            "time_label" : flight.get('DepTime_label'),
            "delay" : {
                "duration" : flight.get('Dep_Delay'),
                "type" : flight.get('Dep_Delay_Type'),
                "factors" : {
                    "carrier" : flight.get('Delay_Carrier'),
                    "weather" : flight.get('Delay_Weather'),
                    "nas" : flight.get("Delay_NAS"),
                    "security" : flight.get('Delay_Security'),
                    "late_aircraft" : flight.get('Delay_LateAircraft')
                }
            },
            "weather" : {
                "prcp" : dep_weather.get('prcp') if dep_weather else None,
                "snow" : dep_weather.get('snow') if dep_weather else None,
                "wdir" : dep_weather.get('wdir') if dep_weather else None,
                "wspd" : dep_weather.get('wspd') if dep_weather else None,
                "pres" : dep_weather.get('pres') if dep_weather else None
            } if dep_weather else {},
            "airport_summary" : {
                "ident" : dep_airport.get('ident') if dep_airport else None,
                "type" : dep_airport.get('type') if dep_airport else None,
                "name" : dep_airport.get('name') if dep_airport else None,
                "elevation_ft" : dep_airport.get('elevation_ft') if dep_airport else None,
                "municipality" : dep_airport.get('municipality') if dep_airport else None,
                "home_link" : dep_airport.get('home_link') if dep_airport else None,
                "local_code" : dep_airport.get('local_code') if dep_airport else None,
                "runway_count" : dep_metrics['runway_count'],
                "max_runway_length_ft" : dep_metrics['max_runway_length_ft'],
                "has_lighted_runway" : dep_metrics['has_lighted_runway'],
                "surfaces" : dep_metrics['surfaces'],
                "frequency_count" : dep_metrics['frequency_count'],
                "has_twr" : dep_metrics['has_twr']
            }
        },
        "arrival" : {
            "airport_code" : arr_iata,
            "city" : flight.get('Arr_CityName') or (arr_geo.get('CITY') if arr_geo else None),
            "delay" : {
                "duration" : flight.get('Arr_Delay')
            },
            "weather" : {
                "prcp" : arr_weather.get('prcp') if arr_weather else None,
                "snow" : arr_weather.get('snow') if arr_weather else None,
                "wdir" : arr_weather.get('wdir') if arr_weather else None,
                "wspd" : arr_weather.get('wspd') if arr_weather else None,
                "pres" : arr_weather.get('pres') if arr_weather else None
            } if arr_weather else {}
        },
        "flight_details" : {
            "duration" : flight.get('Flight_Duration'),
            "distance_type" : flight.get('Distance_type')
        },
        "aircraft" : {
            "manufacturer" : flight.get('Manufacturer'),
            "model" : flight.get('Model'),
            "age" : flight.get('Aircraft_Age')
        },
        "departure_weather_ref" : {
            "airport_id" : dep_iata,
            "date" : flight_date
        },
        "departure_airport_ref" : dep_iata,
        "arrival_airport_ref" : arr_iata
    }

    return document

def create_flights_collection(database, airports_cache, geolocations_cache, runways_cache, airport_frequencies_cache,
                              weather_cache, flight_status_cache, batch_size = 10000, limit = None):
    """
    Function for creating optimized flights collection.
    """

    source_collection = database['us_flights_2023']

    collection = database['flights_hybrid_optimized']
    collection.drop()

    total = source_collection.count_documents({}) if not limit else limit
    cursor = source_collection.find({}).limit(limit) if limit else source_collection.find({})

    documents = []
    inserted = 0
    skipped = 0
    batch_count = 0
    start_time = time.time()

    with tqdm(total = total, desc = "Migrating flights schema", unit = "docs") as pbar:
        for flight in cursor:
            try:
                document = build_optimized_flight_document(flight, airports_cache, geolocations_cache, runways_cache, 
                                                           airport_frequencies_cache, weather_cache, flight_status_cache)

                if document:
                    documents.append(InsertOne(document))

                # Batch insert
                if len(documents) >= batch_size:
                    collection.bulk_write(documents, ordered = False)
                    inserted += len(documents)
                    documents = []
                    batch_count += 1

                    # Update progress bar
                    elapsed = time.time() - start_time
                    docs_per_sec = inserted / elapsed if elapsed > 0 else 0
                    pbar.set_postfix({"batch" : batch_count, "rate" : f"{docs_per_sec:.1f}/s"})
                    pbar.update(batch_size)

            except Exception as e:
                skipped += 1
                print(f"Skipped flight cuz of error: {e}")
                continue

        if documents:
            collection.bulk_write(documents, ordered = False)
            inserted += len(documents)
            pbar.update(len(documents))

    total_time = time.time() - start_time
    print(f"Total time: {total_time:.2f} seconds")

    return collection

def create_optimized_collections(database, batch_size = 10000, limit = None):
    """
    Main function for optimized migration with batch inserts and caching of data in RAM.
    """

    # Cache airport data
    airports_cache = cache_airports(database)

    # Cache airport geolocation data
    airports_geolocations_cache = cache_airport_geolocations(database)

    # Cache runways data
    runways_cache = cache_runways(database)

    # Cache airport frequencies data
    airport_frequencies_cache = cache_airport_frequencies(database)

    # Cache weather data
    weather_cache = cache_weather(database)

    # Cache flight status data
    flight_status_cache = cache_flight_status(database)

    # Create airport summary collection
    airports_summary_collection = create_airport_summary_collection(database, airports_cache, airports_geolocations_cache,
                                                                   runways_cache, airport_frequencies_cache, batch_size)
    
    # Create weather collection
    weather_collection = create_weather_collection(database, weather_cache, batch_size)

    # Create flight collection
    flight_collection = create_flights_collection(database, airports_cache, airports_geolocations_cache, runways_cache,
                                                 airport_frequencies_cache, weather_cache, flight_status_cache, batch_size, limit)

    return {
        "flights" : flight_collection,
        "airports_summary" : airports_summary_collection,
        "weather" : weather_collection
    }
