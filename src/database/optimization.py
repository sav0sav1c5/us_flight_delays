import time
from pymongo import InsertOne
from collections import defaultdict

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
            runways_cache[airport_ident.upper()].append(runway)

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
            "tmin": weather.get('min'),
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

    for flight_status in database['cancelled_diverted_2023'].find({}):

        key = (str(flight_status.get('FlightDate')), flight_status.get('Airline'), flight_status.get('Dep_Airport'), flight_status.get('Arr_Airport'))

        flight_status_cache[key] = {
            "cancelled" : flight_status.get('Cancelled', 0),
            "diverted" : flight_status.get('Diverted', 0)
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

def calculate_airport_summary_metrics(airport, runways_cache, airport_frequencies_cache):
    """
    Function for calculating aggregated metrics for a passed airport.
    """
    ident = airport.get('ident')
    runways = runways_cache.get(ident, [])
    airport_frequencies = airport_frequencies_cache.get(ident, [])

    runway_count = len(runways)

    max_runway_length_ft = max(runway.get('length_ft') for runway in runways) if runways else 0
    
    has_lighted_runway = any((runway.get('lighted') == 1) for runway in runways)
    
    surfaces = sorted({(runway.get('surface') or "") for runway in runways if runway.get('surface')})
    
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

        metrics = calculate_airport_summary_metrics(airport, runways_cache, airport_frequencies_cache)

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
            "runways_count" : metrics['runways_count'],
            "max_runway_length_ft" : metrics['max_runway_lenght_ft'],
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

def create_flights_collection(database, airports_cache, geolocations_cache, runways_cache, airport_frequencies_cache,
                              weather_cache, flight_status_cache, batch_size = 10000):

    pass

def create_optimized_collections(database, batch_size = 10000):
    """
    Function for optimized migration with batch inserts and cachcing of data in RAM.
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
    flight_collection = create_flights_collection(database)

    return {
        "flights" : flight_collection,
        "airports_summary" : airports_summary_collection,
        "weather" : weather_collection
    }

def build_optimized_documents(flights):
    """
    Function for building documents for optimized schema.
    """

    pass
