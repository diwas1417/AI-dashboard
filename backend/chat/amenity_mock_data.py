def get_mock_amenity_data(address):
    """
    Temporary demo data.
    Later we will replace this with Google Places, official sources, council data,
    transport data, crime data, and planning data.
    """

    return {
        "address": address,
        "retail": {
            "nearest_major_retail_km": 2.4,
            "major_store_count": 2,
            "has_pharmacy": True,
            "has_backup_retail": True,
        },
        "transport": {
            "nearest_station_km": 3.2,
            "has_bus_support": True,
            "has_multiple_station_options": False,
        },
        "schools": {
            "nearest_primary_school_km": 1.8,
            "nearest_secondary_school_km": 5.6,
            "primary_school_count_within_5km": 3,
            "secondary_school_count_within_7km": 1,
        },
        "childcare": {
            "nearest_childcare_km": 1.5,
            "childcare_count_within_3km": 4,
            "has_on_estate_childcare": False,
        },
        "medical": {
            "nearest_gp_km": 2.6,
            "nearest_hospital_km": 9.8,
            "medical_services_count_within_4km": 3,
            "has_pharmacy": True,
            "has_urgent_care": False,
        },
        "parks": {
            "nearest_park_km": 0.7,
            "has_playground": True,
            "park_count_within_3km": 4,
            "has_walking_tracks": True,
        },
        "sports": {
            "nearest_sports_facility_km": 2.8,
            "sports_facility_count_within_5km": 3,
            "sports_facility_types": ["oval", "tennis court", "sports reserve"],
        },
        "freeway": {
            "nearest_freeway_entry_km": 4.6,
            "nearest_freeway_name": "Calder Freeway",
        },
        "future_development": {
            "confirmed_future_projects_count": 2,
            "has_major_confirmed_project": False,
            "future_development_certainty": "medium",
        },
        "crime": {
            "crime_level": "manageable",
            "crime_trend": "stable",
        },
    }
