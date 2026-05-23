def clamp_score(score):
    return max(0, min(10, int(score)))


def get_total_interpretation(total_score):
    if total_score <= 39:
        return "Weak"
    if total_score <= 54:
        return "Below average"
    if total_score <= 69:
        return "Moderate / acceptable"
    if total_score <= 79:
        return "Strong"
    if total_score <= 89:
        return "Very strong"
    return "Outstanding"


def score_retail_access(data):
    distance = data.get("nearest_major_retail_km")
    major_store_count = data.get("major_store_count", 0)
    has_pharmacy = data.get("has_pharmacy", False)
    has_backup_retail = data.get("has_backup_retail", False)

    if distance is None:
        return (
            5,
            "Retail Access is scored as average because retail distance is not verified.",
        )

    if distance > 10:
        score = 1
    elif distance > 8:
        score = 2
    elif distance > 6:
        score = 3
    elif distance > 4:
        score = 4
    elif distance > 3:
        score = 5
    elif distance > 2:
        score = 7 if has_pharmacy or has_backup_retail else 6
    elif distance > 1:
        score = 9 if major_store_count >= 2 else 8
    else:
        score = 10

    if major_store_count >= 2 and (has_pharmacy or has_backup_retail):
        score += 1

    score = clamp_score(score)
    return (
        score,
        f"Retail Access = {score} because the nearest major retail option is {distance} km away with {major_store_count} major store(s).",
    )


def score_transport_access(data):
    station_distance = data.get("nearest_station_km")
    has_bus_support = data.get("has_bus_support", False)
    has_multiple_station_options = data.get("has_multiple_station_options", False)

    if station_distance is None:
        return (
            5,
            "Transport Access is scored as average because station distance is not verified.",
        )

    if station_distance > 15:
        score = 1
    elif station_distance > 12:
        score = 2
    elif station_distance > 10:
        score = 3
    elif station_distance > 8:
        score = 4
    elif station_distance > 6:
        score = 5
    elif station_distance > 4:
        score = 6
    elif station_distance > 2:
        score = 7
    elif station_distance > 1:
        score = 9
    else:
        score = 10

    if has_bus_support or has_multiple_station_options:
        score += 1

    score = clamp_score(score)
    return (
        score,
        f"Transport Access = {score} because the nearest train station is {station_distance} km away.",
    )


def score_schools(data):
    primary_km = data.get("nearest_primary_school_km")
    secondary_km = data.get("nearest_secondary_school_km")
    primary_count = data.get("primary_school_count_within_5km", 0)
    secondary_count = data.get("secondary_school_count_within_7km", 0)

    if primary_km is None or secondary_km is None:
        return (
            5,
            "Schools is scored as average because primary or secondary school distance is not verified.",
        )

    if primary_km <= 2 and secondary_km <= 2:
        score = 10
    elif primary_km <= 2 and primary_count >= 2 and secondary_km <= 5:
        score = 9
    elif primary_km <= 2 and secondary_km <= 7:
        score = 8
    elif primary_km <= 2 and secondary_km <= 10:
        score = 7
    elif primary_km <= 5 and secondary_km <= 7:
        score = 6
    elif primary_km <= 10 and secondary_km <= 10:
        score = 5
    elif primary_km <= 10 and secondary_km <= 15:
        score = 4
    elif primary_km <= 6 or secondary_km <= 6:
        score = 3
    elif primary_km <= 8 or secondary_km <= 8:
        score = 2
    else:
        score = 1

    if primary_count >= 2 and secondary_count >= 1:
        score += 1

    score = clamp_score(score)
    return (
        score,
        f"Schools = {score} because the nearest primary school is {primary_km} km away and the nearest secondary school is {secondary_km} km away.",
    )


def score_childcare(data):
    nearest_km = data.get("nearest_childcare_km")
    count_nearby = data.get("childcare_count_within_3km", 0)
    has_on_estate = data.get("has_on_estate_childcare", False)

    if nearest_km is None:
        return (
            5,
            "Childcare is scored as average because childcare distance is not verified.",
        )

    if has_on_estate and count_nearby >= 3:
        score = 10
    elif has_on_estate and count_nearby >= 2:
        score = 9
    elif has_on_estate:
        score = 8
    elif nearest_km <= 3 and count_nearby >= 3:
        score = 7
    elif nearest_km <= 3 and count_nearby >= 2:
        score = 6
    elif nearest_km <= 4 and count_nearby >= 2:
        score = 5
    elif nearest_km <= 4:
        score = 4
    elif nearest_km <= 6:
        score = 3
    elif nearest_km <= 8:
        score = 2
    elif nearest_km <= 10:
        score = 1
    else:
        score = 0

    score = clamp_score(score)
    return (
        score,
        f"Childcare = {score} because the nearest childcare option is {nearest_km} km away with {count_nearby} option(s) within 3 km.",
    )


def score_medical(data):
    nearest_gp_km = data.get("nearest_gp_km")
    hospital_km = data.get("nearest_hospital_km")
    medical_count = data.get("medical_services_count_within_4km", 0)
    has_pharmacy = data.get("has_pharmacy", False)
    has_urgent_care = data.get("has_urgent_care", False)

    if nearest_gp_km is None or hospital_km is None:
        return (
            5,
            "Medical is scored as average because GP or hospital distance is not verified.",
        )

    if nearest_gp_km <= 3 and has_pharmacy and has_urgent_care and hospital_km <= 10:
        score = 10
    elif medical_count >= 3 and hospital_km <= 10:
        score = 9
    elif nearest_gp_km <= 3 and has_pharmacy and has_urgent_care:
        score = 8
    elif nearest_gp_km <= 3 and hospital_km <= 10:
        score = 7
    elif medical_count >= 2 and hospital_km <= 10:
        score = 6
    elif nearest_gp_km <= 4 and hospital_km <= 20:
        score = 5
    elif nearest_gp_km <= 5 and hospital_km <= 20:
        score = 4
    elif nearest_gp_km <= 6 and hospital_km <= 20:
        score = 3
    elif hospital_km <= 30:
        score = 2
    else:
        score = 1

    score = clamp_score(score)
    return (
        score,
        f"Medical = {score} because the nearest GP is {nearest_gp_km} km away and the nearest hospital is {hospital_km} km away.",
    )


def score_parks(data):
    nearest_park_km = data.get("nearest_park_km")
    has_playground = data.get("has_playground", False)
    park_count = data.get("park_count_within_3km", 0)
    has_walking_tracks = data.get("has_walking_tracks", False)

    if nearest_park_km is None:
        return 5, "Parks is scored as average because park distance is not verified."

    if (
        nearest_park_km <= 1
        and park_count >= 3
        and has_playground
        and has_walking_tracks
    ):
        score = 10
    elif (
        nearest_park_km <= 1
        and park_count >= 2
        and has_playground
        and has_walking_tracks
    ):
        score = 9
    elif nearest_park_km <= 1 and park_count >= 2 and has_playground:
        score = 8
    elif nearest_park_km <= 1 and has_playground:
        score = 7
    elif nearest_park_km <= 2 and has_playground:
        score = 5
    elif nearest_park_km <= 2:
        score = 4
    elif nearest_park_km <= 5:
        score = 3
    elif nearest_park_km <= 10:
        score = 2
    elif nearest_park_km <= 15:
        score = 1
    else:
        score = 0

    score = clamp_score(score)
    return (
        score,
        f"Parks = {score} because the nearest park/open space is {nearest_park_km} km away.",
    )


def score_sports_facilities(data):
    nearest_km = data.get("nearest_sports_facility_km")
    facility_count = data.get("sports_facility_count_within_5km", 0)
    facility_types = data.get("sports_facility_types", [])

    if nearest_km is None:
        return (
            5,
            "Sports Facilities is scored as average because sports facility distance is not verified.",
        )

    variety_count = len(facility_types)

    if nearest_km <= 2 and facility_count >= 3 and variety_count >= 3:
        score = 10
    elif nearest_km <= 3 and facility_count >= 3:
        score = 9
    elif nearest_km <= 3 and facility_count >= 2:
        score = 8
    elif nearest_km <= 3:
        score = 7
    elif nearest_km <= 4:
        score = 6
    elif nearest_km <= 5:
        score = 5
    elif nearest_km <= 6:
        score = 3
    else:
        score = 2

    score = clamp_score(score)
    return (
        score,
        f"Sports Facilities = {score} because the nearest sports facility is {nearest_km} km away with {facility_count} option(s) within 5 km.",
    )


def score_freeway_access(data):
    distance = data.get("nearest_freeway_entry_km")
    freeway_name = data.get("nearest_freeway_name", "nearest freeway")

    if distance is None:
        return (
            5,
            "Freeway Access is scored as average because freeway distance is not verified.",
        )

    if distance < 1:
        score = 10
    elif distance <= 2:
        score = 9
    elif distance <= 3:
        score = 8
    elif distance <= 5:
        score = 7
    elif distance <= 7:
        score = 6
    elif distance <= 10:
        score = 5
    elif distance <= 12:
        score = 4
    elif distance <= 15:
        score = 3
    elif distance <= 18:
        score = 2
    else:
        score = 1

    score = clamp_score(score)
    return (
        score,
        f"Freeway Access = {score} because {freeway_name} entry is approximately {distance} km away.",
    )


def score_future_development(data):
    confirmed_projects = data.get("confirmed_future_projects_count", 0)
    has_major_confirmed_project = data.get("has_major_confirmed_project", False)
    evidence_certainty = data.get("future_development_certainty", "medium")

    if confirmed_projects >= 4 and has_major_confirmed_project:
        score = 10
    elif confirmed_projects >= 3 and has_major_confirmed_project:
        score = 9
    elif confirmed_projects >= 3:
        score = 8
    elif confirmed_projects >= 2:
        score = 7
    elif confirmed_projects == 1:
        score = 6
    else:
        score = 5

    if evidence_certainty == "low":
        score -= 1
    elif evidence_certainty == "high":
        score += 1

    score = clamp_score(score)
    return (
        score,
        f"Future Development = {score} because there are {confirmed_projects} confirmed or likely future project(s).",
    )


def score_crime_safety(data):
    crime_level = data.get("crime_level", "moderate")
    trend = data.get("crime_trend", "stable")

    base_scores = {
        "very_high": 1,
        "high": 3,
        "above_average": 4,
        "moderate": 5,
        "manageable": 6,
        "slightly_better": 7,
        "low": 9,
        "very_low": 10,
    }

    score = base_scores.get(crime_level, 5)

    if trend == "improving":
        score += 1
    elif trend == "worsening":
        score -= 1

    score = clamp_score(score)
    return (
        score,
        f"Crime Safety = {score} because the crime level is assessed as {crime_level.replace('_', ' ')} with a {trend} trend.",
    )
