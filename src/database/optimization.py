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

    pass


def build_optimized_documents(flights):
    """
    Function for building documents for optimized schema.
    """

    pass
