import time
from pymongo import InsertOne

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

def create_optimized_collections(database, batch_size = 10000):
    """
    Function for optimized migration with batch inserts and cachcing of data in RAM.
    """

    # Cache airport data
    airports_cache = cache_airports(database)

    # Cache airport geolocation data
    airports_geolocations_cache = cache_airport_geolocations(database)

    pass


def build_optimized_documents(flights):
    """
    Function for building documents for optimized schema.
    """

    pass
