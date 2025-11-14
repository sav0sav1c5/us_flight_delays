
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
    **Query 1:** Which US states have the highest average delays by season (Winter, Spring, Summer, Fall)?
        Data from the **`us_flights_2023`** and **`airports_geolocation`** collections are analyzed.

        The season is determined based on the `flight_date` field:
        * **Winter:** December–February
        * **Spring:** March–May
        * **Summer:** June–August
        * **Fall:** September–November

        The average delay is calculated as `avg(dep_delay)` for all flights from a given state (`state` from `airports_geolocation`) in a given season.

        **Result:** List of US states with average delay by season, sorted in descending order of average delay.
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
                    "$switch" : {
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
                "from" : "airports_geolocation",
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
            "$limit" : 5
        }
    ]

    return pipeline

def get_query_2():
    """
    **Query 2:** Which airlines have the highest average delays on rainy days?
        Collections **`us_flights_2023`** and **`weather_meteo_by_airport`** are used.

        Precipitation is taken from the `prcp' field (mm).

        **Significant precipitation**: days when `prcp > 5.0`.

        Need to find average delay (`avg(dep_delay)`) by airline (`airline`) only for days with significant precipitation, based on weather conditions from `departure.airport_code`.

        **Result:** Airlines with average delay on days with precipitation > 5 mm, sorted in descending order of value.
    """

    pipeline = [
        {
            "$match" : {
                "Dep_Airport" : { "$ne" : None },
                "Dep_Delay" : { "$ne" : None },
                "FlightDate" : { "$ne" : None },
                "Airline" : { "$ne" : None }
            }
        },
        {
            "$lookup" : {
                "from" : "weather_meteo_by_airport",
                "let" : {
                    "dep_airport" : "$Dep_Airport",
                    "flight_date" : "$FlightDate"
                },
                "pipeline" : [
                    {
                        "$match" : {
                            "$expr" : {
                                "$and" : [
                                    { "$eq" : [ "$airport_id", "$$dep_airport"] },
                                    { "$eq" : [ "$time", "$$flight_date"] },
                                    { "$gt" : [ "prcp", 5.0] },
                                    { "$ne" : [ "prcp", None] }
                                ]
                            }
                        }
                    },
                    {"$project": {"_id": 1}}  # Return min data cuz we just need to know if it exists
                ],
                "as" : "weather_info"
            }
        },
        {
            "$group" : {
                "_id" : "$Airline",
                "average_delay" : { "$avg" : "Dep_Delay" },
                "flight_count" : { "$sum" : 1 },
                "total_delay_min" : { "$sum" : "Dep_Delay" }
            }
        },
        {
            "$sort" : { "average_delay" : -1}
        },
        {
            "$limit" : 5
        }
    ]

    return pipeline

def get_query_3():
    """
    **Query 3:** Which airports have the most canceled flights during bad weather?
        Collections **`cancelled_deverted_2023`**, **`weather_meteo_by_airport`** and **`airports_geolocation`** are used.

        Canceled flights are those with `cancelled = 1`.

        **Bad weather conditions** are defined as:
        * `prcp > 10 mm' *(heavy precipitation)*
        * **or** `wspd > 15 m/s' *(strong wind)*

        The query should match ($lookup) flights and weather data by `dep_airport` and `airport_id`.

        **Result:** Airports with the highest number of canceled flights during bad weather, sorted in descending order of cancellations.
    """

    pipeline = [
        {
            "$match" : {
                "Dep_Airport" : { "$ne" : None },
                "FlightDate" : { "$ne" : None },
                "Dep_Delay" : { "$ne" : None },
                "Cancelled" : { "$eq" : 1 }
            }
        },
        {
            "$lookup" : {
                "from" : "weather_meteo_by_airport",
                "let" : {
                    "dep_airport" : "$Dep_Airport",
                    "flight_date" : "$FlightDate"
                },
                "pipeline" : [
                    {
                        "$match" : {
                            "$expr" : {
                                "$and" : [
                                    { "$eq" : [ "$airport_id", "$$dep_airport" ]},
                                    { "$eq" : [ "$time", "$$flight_date" ]},
                                    { "$or" : [
                                        { "$gt" : [ "$prcp", 5.0]},
                                        { "$gt" : [ "$wspd", 15]}
                                    ]}
                                ]
                            }
                        }
                    },
                    {
                        "$project" : { "_id" : 1 }
                    }
                ],
                "as" : "weather_info"
            }
        },
        {
            "$match": {
                "weather_info" : {"$ne" : [] }
            }
        },
        {
            "$lookup" : {
                "from" : "airports_geolocation",
                "localField" : "Dep_Airport",
                "foreignField" : "IATA_CODE",
                "as" : "airport_info"
            }
        },

        {
            "$group" : {
                "_id" : "$Dep_Airport",
                "cancelled_flights_count" : { "$sum" : 1 },
                "city" : { "$first" : "$airport_info.CITY" }
            }
        },
        { 
            "$sort" : { "cancelled_flights_count" : -1 }
        }
    ]

    return pipeline

def get_query_4():
    """
    **Query 4:** Do airports with more diverse runways have lower average delays?
        Collections **`airports`**, **`runways`**, and **`us_flights_2023`** are used.

        For each airport, the following is calculated:
        * **Runway Diversity Index (RDI)** = number of different values ​​of `surface` from the collection of `runways` per airport.
        * **Average Delay** = average `dep_delay` from `us_flights_2023` per airport.

        It is necessary to merge (`$lookup') all three collections, calculate both metrics, and analyze whether airports with higher RDI have lower average delays.

        **Result:** List of airports with RDI and average delay, sorted in ascending order of average delay.
    """

    pipeline = [
        {
            "$match" : {
                "iata_code" : { "$ne" : None },
                "type" : { "$in" : ["medium_airport", "large_airport"]}
            }
        },
        {
            "$lookup" : {
                "from" : "runways",
                "localField" : "ident",
                "foreignField" : "airport_ident",
                "as" : "runway_info"
            },
        },
        {
            "$lookup" : {
                "from" : "us_flights_2023",
                "let" : {
                    "airport_code" : "$iata_code"
                },
                "pipeline" : [
                    {
                        "$match" : {
                            "$expr" : {
                                "$eq" : [ "$Dep_Airport", "$$airport_code" ]
                            }
                        }
                    },
                    {
                        "$group" : {
                            "_id" : "$Dep_Airport",
                            "average_delay" : { "$avg" : "$Dep_Delay" },
                            "total_flights" : { "$sum" : 1 }
                        }
                    }
                ],
                "as" : "flight_info"
            }
        },
        {
            "$match" : {
                "runway_info" : { "$ne" : [] },
                "flight_info" : { "$ne" : [] }
            }
        },
        {
            "$addFields" : { 
                "RDI": { 
                    "$size": { 
                        "$setUnion": [
                            { "$map": { 
                                "input": "$runway_info", 
                                "as": "runway", 
                                "in": "$$runway.surface"
                            }}, 
                            [] 
                        ] 
                    } 
                }
            }
        },
        {
            "$project" : {
                "airport_code" : "$iata_code",
                "airport_name" : "$name",
                "RDI" : 1,
                "average_delay" : {
                    "$round" : [ { "$arrayElemAt": ["$flight_info.average_delay", 0] }, 2] 
                },
                "total_flights": { 
                    "$arrayElemAt": ["$flight_info.total_flights", 0] 
                },
                "runway_surfaces": {
                    "$map": {
                        "input": "$runway_info",
                        "as": "runway",
                        "in": "$$runway.surface"
                    }
                }
            }
        },
        {
            "$sort" : { "average_delay" : -1, "total_flights" : -1 }
        }
    ]

    return pipeline

def get_query_5():
    """
    **Query 5:** Which airlines are most affected by **weather-related delays** at **high-elevation airports** with **complex communication frequency environments**?
        This query uses collections: **`us_flights_2023`**, **`airports`**, and **`airport_frequencies`**.

        Which airlines have the most weather-related delays (weather delay > 10 minutes), for flights from airports with an altitude of more than 500 feet and more than 5 communication frequencies?
        
        We analyze how **weather delays** vary across airlines **depending on characteristics of the airports they operate from** and return **top 10** airlines most affected. 

        **Result:**  A ranked list of airlines operating in **high-elevation, high-complexity airports**, showing how strongly **weather delays** affect them. 
    """

    pipeline = [
        {
            "$match" : {
                "Dep_Airport" : { "$ne" : None },
                "FlightDate" : { "$ne" : None },
                "Dep_Delay" : { "$ne" : None },
                "Airline" : { "$ne" : None },
                "Delay_Weather" : { "$gt" : 10, "$ne" : None }
            }
        },
        {
            "$group" : {
                "_id" : {
                    "airline" : "$Airline",
                    "airport" : "$Dep_Airport"
                },
                "weather_delay_count" : { "$sum" : 1 },
                "total_weather_delay" : { "$sum" : "$Delay_Weather" },
                "average_weather_delay" : { "$avg" : "$Delay_Weather" }
            }
        },
        {
            "$match" : {
                "weather_delay_count" : { "$gt" : 50 } 
            }
        },
        {
            "$lookup" : {
                "from" : "airports",
                "let" : {
                    "airport_code" : "$_id.airport"
                },
                "pipeline" : [
                    {
                        "$match" : {
                            "$expr" : {
                                "$eq" : ["$iata_code", "$$airport_code"]
                            },
                            "ident" : { "$ne" : None },
                            "elevation_ft" : { "$gt" : 500, "$ne" : None }
                        }
                    }
                ],
                "as" : "airport_info"
            }
        },
        {
            "$match" : {
                "airport_info" : { "$ne" : [] }
            }
        },
        {
            "$unwind" : "$airport_info"
        },
        {
            "$lookup" : {
                "from" : "airport_frequencies",
                "let" : { "airport_ident" : "$airport_info.ident" },
                "pipeline" : [
                    {
                        "$match" : {
                            "$expr" : {
                                "$eq" : [ "$airport_ident", "$$airport_ident" ]
                            }
                        }
                    },
                    {
                        "$group" : {
                            "_id" : "$airport_ident",
                            "frequency_count" : { "$sum" : 1 }
                        }
                    }
                ],
                "as" : "airport_freq_info"
            }
        },
        {
            "$match": {
                "airport_freq_info": { "$ne": [] }
            }
        },
        {
            "$unwind": "$airport_freq_info"
        },
        {
            "$match": {
                "airport_freq_info.frequency_count": { "$gt": 5 }
            }
        },
        {
            "$group" : {
                "_id" : "$_id.airline",
                "total_weather_delays": {"$sum": "$weather_delay_count"},
                "avg_delay_minutes": {"$avg": "$average_weather_delay"},
                "total_delay_minutes": {"$sum": "$total_weather_delay"},
                "affected_airports": {"$addToSet": "$_id.airport"},
                "avg_elevation": {"$avg": "$airport_info.elevation_ft"},
                "total_frequencies": {"$avg": "$airport_freq_info.frequency_count"}
            }
        },
        {
            "$sort" : { "total_weather_delays" : -1 }
        }
    ]

    return pipeline