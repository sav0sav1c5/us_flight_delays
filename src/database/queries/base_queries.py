
def get_base_queries():

    return {
        "query_1" : get_query_1(),
        "query_2" : get_query_2(),
        "query_3" : get_query_3(),
        "query_4" : get_query_4(),
        "query_5" : get_query_5()
    }

def get_query_1():
    """
    **Upit 1:** Koje američke države imaju najveća prosečna kašnjenja po sezonama (Winter, Spring, Summer, Fall)?  
        - Analizira se sezonalnost kašnjenja — da li se kašnjenja razlikuju po godišnjim dobima.  
        - Koriste se kolekcije `us_flights_2023` i `airports_geolocation`. 
    """

    pass

def get_query_2():
    """
    **Upit 2:** Koje avio-kompanije imaju najveća prosečna kašnjenja tokom dana sa padavinama?  
        - Cilj je proceniti uticaj vremenskih uslova na tačnost letova po avio-kompanijama.  
        - Koriste se kolekcije `us_flights_2023` i `weather_meteo_by_airport`.  
        - **Značajne padavine:** definišu se kao `prcp > 5 mm`, što meteorološki označava **umerene do jake padavine**.  
    """

    pass

def get_query_3():
    """
    **Upit 3:** Koji aerodromi imaju najviše otkazanih letova tokom loših vremenskih uslova?  
        - Povezuje informacije o otkazanim letovima i meteorološkim uslovima.  
        - Koriste se kolekcije `us_flights_2023`, `weather_meteo_by_airport` i `airports_geolocation`.  
        - **Loše vreme:** definisano kao:
            - `prcp > 10 mm` → jake ili vrlo jake padavine  
            - `wspd > 15 m/s` → jak do olujni vetar  
    """

    pass

def get_query_4():
    """
    **Upit 4:** Da li aerodromi sa raznovrsnijim pistama imaju manja prosečna kašnjenja?  
        - Analizira vezu između infrastrukture aerodroma i efikasnosti letova.  
        - Koriste se kolekcije `airports`, `runways` i `us_flights_2023`.  
        - Uvodi se **Runway Diversity Index (RDI)**:
            - predstavlja broj različitih površina pista (`surface`) po aerodromu.  
    """

    pass

def get_query_5():
    """
    **Upit 5:** Kako se performanse avio-kompanija razlikuju po tipu udaljenosti leta (Short, Medium, Long Haul)?  
        - Poredi prosečna kašnjenja po tipu rute (`distance_type`).  
        - Koristi se kolekcija `us_flights_2023`. 
    """

    pass