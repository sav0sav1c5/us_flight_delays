
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
                "city" : { "$first" : "$airport_info.CITY" },
                "state" : { "$first" : "$airport_info.STATE" }
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
    **Query 5:** How does airline performance differ by type of flight distance (Short, Medium, Long Haul)?
        Collection **`us_flights_2023`** is used.
        - `distance_type' indicates the flight length category.

        For each airline (`airline`) the average delay (`avg(arr_delay)`) is calculated, grouped by `distance_type`.

        **Result:** A table with airlines and average delay by route type, sorted descending by average delay within each category.
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