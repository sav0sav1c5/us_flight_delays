
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

    pipeline = [
        {
            "$match" : {
                "Dep_Airport" : { "$ne" : None },
                "Dep_Delay" : { "$ne" : None },
                "FlightDate" : { "$ne" : None }
            }
        },
        {
            "$addFields" : {
                "month" : { "$toInt" : { "$substr" : [ "$FlightDate", 5, 2]}}
            }
        },
        {
            "$addFields" : {
                "season" : {
                    "#switch" : {
                        "branches" : [
                            {
                                "case" : { "$in" : [ "$month", [12, 1, 2]] },
                                "then" : "Winter"
                            },
                            {
                                "case" : { "$in" : [ "$month", [3, 4, 5]] },
                                "then" : "Spring"
                            },
                            {
                                "case" : { "$in" : [ "$month", [6, 7, 8]] },
                                "then" : "Summer"
                            },
                            {
                                "case" : { "$in" : [ "$month", [9, 10, 11]] },
                                "then" : "Autumn"
                            }                            
                        ],
                        "default" : "Unknown"
                    }
                }
            }
        },
        {
            "$lookup" : {
                "from" : "airport_geolocation",
                "localField" : "Dep_Airport",
                "foreignField" : "IATA_CODE",
                "as" : "geolocation_info"
            }
        },
        {
            "$unwind" : {
                "path" : "$geolocation_info",
                "preserveNullAndEmptyArrays" : False        # Remove flight witout geolocation info
            }
        },
        {
            "$group" : {
                "_id" : {
                    "state" : "$geolocation_info.state",
                    "season" : "$season"
                },
                "average_delay" : { "$avg" : "$Dep_Delay" },
                "flight_count" : { "$sum" : 1}
            }
        },
        {
            "$project" : {
                "_id" : 0,                              # Dont show id
                "state" : "$_id.state",                 # Show state pulled from _id  
                "season" : "$_id.season",
                "average_delay" : {
                    "$round" : [ "$average_delay", 2]   # Avg. delay with 2 decimal
                },
                "flight_count" : 1                     # Show flight count
            }
        },
        {
            "$sort" : {
                "average_delay" : -1,
                "flight_count" : -1 
            }
        },
        {
            "$limit" : 10
        }
    ]

    return pipeline

def get_query_2():
    """
    **Upit 2:** Koje avio-kompanije imaju najveća prosečna kašnjenja tokom dana sa padavinama?  
        - Cilj je proceniti uticaj vremenskih uslova na tačnost letova po avio-kompanijama.  
        - Koriste se kolekcije `us_flights_2023` i `weather_meteo_by_airport`.  
        - **Značajne padavine:** definišu se kao `prcp > 5 mm`, što meteorološki označava **umerene do jake padavine**.  
    """

    pipeline = [

    ]

    return pipeline

def get_query_3():
    """
    **Upit 3:** Koji aerodromi imaju najviše otkazanih letova tokom loših vremenskih uslova?  
        - Povezuje informacije o otkazanim letovima i meteorološkim uslovima.  
        - Koriste se kolekcije `us_flights_2023`, `weather_meteo_by_airport` i `airports_geolocation`.  
        - **Loše vreme:** definisano kao:
            - `prcp > 10 mm` → jake ili vrlo jake padavine  
            - `wspd > 15 m/s` → jak do olujni vetar  
    """

    pipeline = [

    ]

    return pipeline

def get_query_4():
    """
    **Upit 4:** Da li aerodromi sa raznovrsnijim pistama imaju manja prosečna kašnjenja?  
        - Analizira vezu između infrastrukture aerodroma i efikasnosti letova.  
        - Koriste se kolekcije `airports`, `runways` i `us_flights_2023`.  
        - Uvodi se **Runway Diversity Index (RDI)**:
            - predstavlja broj različitih površina pista (`surface`) po aerodromu.  
    """

    pipeline = [
        {

        },
        {

        },
        {

        },
        {

        },
        {

        },
        {

        },
    ]

    return pipeline

def get_query_5():
    """
    **Upit 5:** Kako se performanse avio-kompanija razlikuju po tipu udaljenosti leta (Short, Medium, Long Haul)?  
        - Poredi prosečna kašnjenja po tipu rute (`distance_type`).  
        - Koristi se kolekcija `us_flights_2023`. 
    """

    pipeline = [
        {

        },
        {

        },
        {

        },
        {

        },
        {

        },
        {

        },
    ]

    return pipeline