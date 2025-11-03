# Schemas

Three different schemas tried:
- **Base Schema**
- **One-Collection Schema**
- **Hybrid Schema**

## I. Base schema

Base schema used was created using **two datasets** and **contain 7 different collections**.

### Collection 1: `us_flights_2023`

```json
{
  "_id": "68ed816347af4980cf38824a",
  "flight_date": "2023-01-02",
  "day_of_week": 1,
  "airline": "Endeavor Air",
  "tail_number": "N605LR",
  "dep_airport": "BDL",
  "dep_city_name": "Hartford, CT",
  "dep_time_label": "Morning",
  "dep_delay": -3,
  "dep_delay_tag": 0,
  "dep_delay_type": "Low <5min",
  "arr_airport": "LGA",
  "arr_city_name": "New York, NY",
  "arr_delay": -12,
  "arr_delay_type": "Low <5min",
  "flight_duration": 56,
  "distance_type": "Short Haul >1500Mi",
  "delay_carrier": 0,
  "delay_weather": 0,
  "delay_nas": 0,
  "delay_security": 0,
  "delay_last_aircraft": 0,
  "manufacturer": "CANADAIR REGIONAL JET",
  "model": "CRJ",
  "aicraft_age": 16
}
```

### Collection 2: `cancelled_deverted_2023`

```json
{
  "_id": "68ed80cdb872eb7f8ad2c324",
  "flight_date": "2023-01-25",
  "day_of_week": 3,
  "airline": "Endeavor Air",
  "tail_number": "N691CA",
  "cancelled": 1.0,
  "diverted": 0.0,
  "dep_airport": "JFK",
  "dep_city_name": "New York, NY",
  "dep_time_label": "Evening",
  "dep_delay": 0.0,
  "dep_delay_tag": 0,
  "dep_delay_type": "No Departure Delay",
  "arr_airport": "ITH",
  "arr_city_name": "Ithaca/Cortland, NY",
  "arr_delay": 0.0,
  "arr_delay_type": "No Arrival Delay",
  "flight_duration": 0.0,
  "distance_type": "Short Haul",
  "delay_carrier": 0.0,
  "delay_weather": 0.0,
  "delay_nas": 0.0,
  "delay_security": 0.0,
  "delay_last_aircraft": 0.0
}
```

### Collection 3: `weather_meteo_by_airport`

```json
{
  "_id": "68ed80cdb872eb7f8ad2ea34",
  "time": "2023-01-01",
  "tavg": 8.1,
  "tmin": 2.2,
  "tmax": 11.7,
  "prcp": 0.0,
  "snow": 0.0,
  "wdir": 278.0,
  "wspd": 9.7,
  "pres": 1013.8,
  "airport_id": "ABE"
}

```

### Collection 4: `airports_geolocation`

```json
{
  "_id": "68ed8455a82cf2247e50b79a",
  "iata_code": "ABE",
  "airport": "Lehigh Valley International Airport",
  "city": "Allentown",
  "state": "PA",
  "country": "USA",
  "latitude": 40.65236,
  "longitude": -75.4404
}
```

### Collection 5: `airports`

```json
{
  "_id": "68ed80cdb872eb7f8ad31144",
  "id": 6523,
  "ident": "00A",
  "type": "heliport",
  "name": "Total Rf Heliport",
  "latitude_deg": 40.07080078125,
  "longitude_deg": -74.93360137939453,
  "elevation_ft": 11.0,
  "continent": null,
  "iso_country": "US",
  "iso_region": "US-PA",
  "municipality": "Bensalem",
  "scheduled_service": "no",
  "gps_code": "00A",
  "iata_code": null,
  "local_code": "00A",
  "home_link": null,
  "wikipedia_link": null,
  "keywords": null
}
```

### Collection 6: `airport_frequencies`

```json
{
  "_id": "68ed80cdb872eb7f8ad33854",
  "id": 70518,
  "airport_ref": 6528,
  "airport_ident": "00CA",
  "type": "CTAF",
  "description": "CTAF",
  "frequency_mhz": 122.9
}
```

### Collection 7: `runways`

```json
{
  "_id": "68ed80ceb872eb7f8ad35f64",
  "id": 269408,
  "airport_ref": 6523,
  "airport_ident": "00A",
  "length_ft": 80,
  "width_ft": 80.0,
  "surface": "ASPH-G",
  "lighted": 1,
  "closed": 0,
  "le_ident": "H1",
  "le_latitude_deg": NaN,
  "le_longitude_deg": NaN,
  "le_elevation_ft": NaN,
  "le_heading_degT": NaN,
  "le_displaced_threshold_ft": NaN,
  "he_ident": null,
  "he_latitude_deg": NaN,
  "he_longitude_deg": NaN,
  "he_elevation_ft": NaN,
  "he_heading_degT": NaN,
  "he_displaced_threshold_ft": NaN
}
```

## II. One-Collection Schema

Contain just **one collection with embedded documents of other collections**.

### Collection 1: `us_flights_optimized`

```json
{
  "_id": "690403d3ca815ec0963c9ecc",
  "flight_id": "Endeavor Air_2023-01-02 00:00:00_BDL_LGA",
  "flight_date": "2023-01-02 00:00:00",
  "day_of_week": 1,
  "airline": "Endeavor Air",
  "tail_number": null,
  "status": {
    "cancelled": 0,
    "diverted": 0
  },
  "departure": {
    "airport_code": "BDL",
    "city": "Hartford, CT",
    "time_label": "Morning",
    "location": {
      "city": "Windsor Locks",
      "state": "CT",
      "country": "USA",
      "lat": 41.93887,
      "lon": -72.68323
    },
    "delay": {
      "duration": -3,
      "tag": 0,
      "type": "Low <5min",
      "factors": {
        "carrier": 0,
        "weather": 0,
        "nas": 0,
        "security": 0,
        "late_aircraft": 0
      }
    },
    "weather": {
      "tavg": 2.9,
      "tmin": -2.1,
      "tmax": 8.3,
      "prcp": 0.0,
      "snow": 0.0,
      "wdir": 338.0,
      "wspd": 3.2,
      "pres": 1019.1
    },
    "airport_summary": {
      "ident": "KBDL",
      "type": "large_airport",
      "name": "Bradley International Airport",
      "elevation_ft": 173.0,
      "municipality": "Hartford",
      "home_link": "http://www.bradleyairport.com/",
      "runway_count": 3,
      "max_runway_length_ft": 9510,
      "has_lighted_runway": true,
      "frequency_count": 12,
      "has_twr": true
    },
    "runways": [
      {
        "runway_id": "245310",
        "length_ft": 5145,
        "width_ft": 100,
        "surface": "ASP",
        "lighted": 1,
        "closed": 0,
        "le_ident": 1,
        "le_displaced_threshold_ft": null,
        "he_ident": 19,
        "he_displaced_threshold_ft": null
      },
      {
        "runway_id": "245311",
        "length_ft": 9510,
        "width_ft": 200,
        "surface": "ASP",
        "lighted": 1,
        "closed": 0,
        "le_ident": 6,
        "le_displaced_threshold_ft": null,
        "he_ident": 24,
        "he_displaced_threshold_ft": null
      },
      {
        "runway_id": "245312",
        "length_ft": 6847,
        "width_ft": 150,
        "surface": "ASP",
        "lighted": 1,
        "closed": 0,
        "le_ident": 15,
        "le_displaced_threshold_ft": null,
        "he_ident": 33,
        "he_displaced_threshold_ft": null
      }
    ],
    "frequencies": [
      {
        "type": "APP",
        "description": "APP",
        "frequency_mhz": 32.58
      },
      {
        "type": "APP",
        "description": "APP",
        "frequency_mhz": 123.95
      },
      {
        "type": "ATIS",
        "description": "ATIS",
        "frequency_mhz": 118.15
      },
      {
        "type": "CLD",
        "description": "CLNC DEL",
        "frequency_mhz": 121.75
      },
      {
        "type": "DEP",
        "description": "DEP",
        "frequency_mhz": 35.9
      },
      {
        "type": "DEP",
        "description": "DEP",
        "frequency_mhz": 123.95
      },
      {
        "type": "GND",
        "description": "GND",
        "frequency_mhz": 121.9
      },
      {
        "type": "MISC",
        "description": "ARNG OPS",
        "frequency_mhz": 41.9
      },
      {
        "type": "OPS",
        "description": "ANG OPS",
        "frequency_mhz": 138.55
      },
      {
        "type": "RDO",
        "description": "BRIDGEPORT RDO",
        "frequency_mhz": 122.3
      },
      {
        "type": "TWR",
        "description": "TWR",
        "frequency_mhz": 120.3
      },
      {
        "type": "UNIC",
        "description": "UNICOM",
        "frequency_mhz": 122.95
      }
    ]
  },
  "arrival": {
    "airport_code": "LGA",
    "city": "New York, NY",
    "time_label": null,
    "location": {
      "city": "New York",
      "state": "NY",
      "country": "USA",
      "lat": 40.77724,
      "lon": -73.87261
    },
    "delay": {
      "duration": -12,
      "tag": null,
      "type": "Low <5min",
      "factors": null
    },
    "weather": {
      "tavg": 11.4,
      "tmin": 9.4,
      "tmax": 13.3,
      "prcp": 0.5,
      "snow": 0.0,
      "wdir": 265.0,
      "wspd": 6.8,
      "pres": 1019.7
    },
    "airport_summary": {
      "ident": "KLGA",
      "type": "large_airport",
      "name": "La Guardia Airport",
      "elevation_ft": 21.0,
      "municipality": "New York",
      "home_link": "https://www.laguardiaairport.com/",
      "runway_count": 3,
      "max_runway_length_ft": 7000,
      "has_lighted_runway": true,
      "frequency_count": 8,
      "has_twr": true
    },
    "runways": [
      {
        "runway_id": "243692",
        "length_ft": 7000,
        "width_ft": 150,
        "surface": "ASP",
        "lighted": 1,
        "closed": 0,
        "le_ident": 4,
        "le_displaced_threshold_ft": null,
        "he_ident": 22,
        "he_displaced_threshold_ft": null
      },
      {
        "runway_id": "243693",
        "length_ft": 7000,
        "width_ft": 150,
        "surface": "ASP",
        "lighted": 1,
        "closed": 0,
        "le_ident": 13,
        "le_displaced_threshold_ft": null,
        "he_ident": 31,
        "he_displaced_threshold_ft": null
      },
      {
        "runway_id": "333613",
        "length_ft": 60,
        "width_ft": 60,
        "surface": "ASP",
        "lighted": 0,
        "closed": 0,
        "le_ident": "H1",
        "le_displaced_threshold_ft": null,
        "he_ident": "H1",
        "he_displaced_threshold_ft": null
      }
    ],
    "frequencies": [
      {
        "type": "APP",
        "description": "NEW YORK APP",
        "frequency_mhz": 118
      },
      {
        "type": "APP",
        "description": "NEW YORK APP",
        "frequency_mhz": 132.7
      },
      {
        "type": "ATIS",
        "description": "ATIS",
        "frequency_mhz": 125.95
      },
      {
        "type": "CLD",
        "description": "CLNC DEL",
        "frequency_mhz": 121.875
      },
      {
        "type": "DEP",
        "description": "NEW YORK DEP",
        "frequency_mhz": 120.4
      },
      {
        "type": "GND",
        "description": "GND",
        "frequency_mhz": 121.7
      },
      {
        "type": "TWR",
        "description": "TWR",
        "frequency_mhz": 118.7
      },
      {
        "type": "UNIC",
        "description": "UNICOM",
        "frequency_mhz": 122.95
      }
    ]
  },
  "flight_details": {
    "duration": 56,
    "distance_type": "Short Haul >1500Mi"
  },
  "aircraft": {
    "manufacturer": "CANADAIR REGIONAL JET",
    "model": "CRJ",
    "age": 16
  }
}
```

## III. Hybrid Schema

Optimized hybrid schema contains **tree new collections** adjusted for best query performances.

### Collection 1: `flights_hybrid_optimized`

```json
{
  "_id": "68f3cb5618077042a6bddff0",
  "flight_id": "Endeavor Air_2023-01-02 00:00:00_BDL_LGA",
  "flight_date": "2023-01-02 00:00:00",
  "day_of_week": 1,
  "airline": "Endeavor Air",
  "tail_number": null,
  "status": {
    "cancelled": 0,
    "diverted": 0
  },
  "departure": {
    "airport_code": "BDL",
    "city": "Hartford, CT",
    "time_label": "Morning",
    "delay": {
      "duration": -3,
      "type": "Low <5min",
      "factors": {
        "carrier": null,
        "weather": null,
        "nas": null,
        "security": null,
        "late_aircraft": null
      }
    },
    "weather": {
      "prcp": 0.0,
      "snow": 0.0,
      "wdir": 338.0,
      "wspd": 3.2,
      "pres": 1019.1
    },
    "airport_summary": {
      "ident": "KBDL",
      "type": "large_airport",
      "name": "Bradley International Airport",
      "elevation_ft": 173.0,
      "municipality": "Hartford",
      "home_link": "http://www.bradleyairport.com/",
      "runway_count": 3,
      "max_runway_length_ft": 9510,
      "has_lighted_runway": true,
      "frequency_count": 12,
      "has_twr": true
    }
  },
  "arrival": {
    "airport_code": "LGA",
    "city": "New York, NY",
    "delay": {
      "duration": -12
    },
    "weather": {
      "prcp": 0.5,
      "snow": 0.0,
      "wdir": 265.0,
      "wspd": 6.8,
      "pres": 1019.7
    }
  },
  "flight_details": {
    "duration": 56,
    "distance_type": "Short Haul >1500Mi"
  },
  "aircraft": {
    "manufacturer": "CANADAIR REGIONAL JET",
    "model": "CRJ",
    "age": 16
  },
  "departure_weather_ref": {
    "airport_id": "BDL",
    "date": "2023-01-02 00:00:00"
  },
  "departure_airport_ref": "BDL",
  "arrival_airport_ref": "LGA"
}
```

### Collection 2: `airports_summary_hybrid_optimized`

```json
{
  "_id": "68f3cb4718077042a6bbcdfd",
  "iata": "OCA",
  "ident": "07FA",
  "type": "small_airport",
  "name": "Ocean Reef Club Airport",
  "elevation_ft": 8.0,
  "municipality": "Key Largo",
  "country": null,
  "home_link": "https://www.oceanreef.com/community/private-airport-1345.html",
  "local_code": "07FA",
  "runway_count": 1,
  "max_runway_length_ft": 4500,
  "has_lighted_runway": true,
  "surfaces": [
    "ASPH"
  ],
  "frequency_count": 1,
  "has_twr": false
}
```

### Collection 3: `weather_hybrid_optimized`

```json
{
  "_id": "68f3cb4718077042a6bbd8f4",
  "airport_id": "ABE",
  "date": "2023-01-01 00:00:00",
  "tavg": 8.1,
  "tmin": 2.2,
  "tmax": 11.7,
  "prcp": 0.0,
  "snow": 0.0,
  "wdir": 278.0,
  "wspd": 9.7,
  "pres": 1013.8
}
```