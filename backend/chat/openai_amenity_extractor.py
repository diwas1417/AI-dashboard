import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


AMENITY_INPUT_SCHEMA = {
    "name": "amenity_inputs",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "retail": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "nearest_major_retail_km": {"type": ["number", "null"]},
                    "major_store_count": {"type": "integer"},
                    "has_pharmacy": {"type": "boolean"},
                    "has_backup_retail": {"type": "boolean"},
                },
                "required": [
                    "nearest_major_retail_km",
                    "major_store_count",
                    "has_pharmacy",
                    "has_backup_retail",
                ],
            },
            "transport": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "nearest_station_km": {"type": ["number", "null"]},
                    "has_bus_support": {"type": "boolean"},
                    "has_multiple_station_options": {"type": "boolean"},
                },
                "required": [
                    "nearest_station_km",
                    "has_bus_support",
                    "has_multiple_station_options",
                ],
            },
            "schools": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "nearest_primary_school_km": {"type": ["number", "null"]},
                    "nearest_secondary_school_km": {"type": ["number", "null"]},
                    "primary_school_count_within_5km": {"type": "integer"},
                    "secondary_school_count_within_7km": {"type": "integer"},
                },
                "required": [
                    "nearest_primary_school_km",
                    "nearest_secondary_school_km",
                    "primary_school_count_within_5km",
                    "secondary_school_count_within_7km",
                ],
            },
            "childcare": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "nearest_childcare_km": {"type": ["number", "null"]},
                    "childcare_count_within_3km": {"type": "integer"},
                    "has_on_estate_childcare": {"type": "boolean"},
                },
                "required": [
                    "nearest_childcare_km",
                    "childcare_count_within_3km",
                    "has_on_estate_childcare",
                ],
            },
            "medical": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "nearest_gp_km": {"type": ["number", "null"]},
                    "nearest_hospital_km": {"type": ["number", "null"]},
                    "medical_services_count_within_4km": {"type": "integer"},
                    "has_pharmacy": {"type": "boolean"},
                    "has_urgent_care": {"type": "boolean"},
                },
                "required": [
                    "nearest_gp_km",
                    "nearest_hospital_km",
                    "medical_services_count_within_4km",
                    "has_pharmacy",
                    "has_urgent_care",
                ],
            },
            "parks": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "nearest_park_km": {"type": ["number", "null"]},
                    "has_playground": {"type": "boolean"},
                    "park_count_within_3km": {"type": "integer"},
                    "has_walking_tracks": {"type": "boolean"},
                },
                "required": [
                    "nearest_park_km",
                    "has_playground",
                    "park_count_within_3km",
                    "has_walking_tracks",
                ],
            },
            "sports": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "nearest_sports_facility_km": {"type": ["number", "null"]},
                    "sports_facility_count_within_5km": {"type": "integer"},
                    "sports_facility_types": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": [
                    "nearest_sports_facility_km",
                    "sports_facility_count_within_5km",
                    "sports_facility_types",
                ],
            },
            "freeway": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "nearest_freeway_entry_km": {"type": ["number", "null"]},
                    "nearest_freeway_name": {"type": "string"},
                },
                "required": ["nearest_freeway_entry_km", "nearest_freeway_name"],
            },
            "future_development": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "confirmed_future_projects_count": {"type": "integer"},
                    "has_major_confirmed_project": {"type": "boolean"},
                    "future_development_certainty": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                    },
                },
                "required": [
                    "confirmed_future_projects_count",
                    "has_major_confirmed_project",
                    "future_development_certainty",
                ],
            },
            "crime": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "crime_level": {
                        "type": "string",
                        "enum": [
                            "very_high",
                            "high",
                            "above_average",
                            "moderate",
                            "manageable",
                            "slightly_better",
                            "low",
                            "very_low",
                        ],
                    },
                    "crime_trend": {
                        "type": "string",
                        "enum": ["worsening", "stable", "improving"],
                    },
                },
                "required": ["crime_level", "crime_trend"],
            },
        },
        "required": [
            "retail",
            "transport",
            "schools",
            "childcare",
            "medical",
            "parks",
            "sports",
            "freeway",
            "future_development",
            "crime",
        ],
    },
    "strict": True,
}


def extract_amenity_inputs_with_openai(address, raw_research_text):
    """
    Converts raw amenity research text into clean JSON inputs for our scoring engine.
    OpenAI should not invent values. Unknown distances must be null.
    """

    prompt = f"""
You are converting suburb amenity research notes into structured JSON for a scoring engine.

Address:
{address}

Raw research notes:
{raw_research_text}

Rules:
- Use only the raw research notes provided.
- Do not search the web.
- Do not guess missing distances.
- If a distance is missing or unclear, use null.
- If a count is missing, use 0.
- If a boolean is unclear, use false.
- Distances must be numbers in kilometres.
- Return only data that matches the schema.
"""

    response = client.responses.create(
        model="gpt-5.5",
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": AMENITY_INPUT_SCHEMA["name"],
                "schema": AMENITY_INPUT_SCHEMA["schema"],
                "strict": True,
            }
        },
    )

    return json.loads(response.output_text)
