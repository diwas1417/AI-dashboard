import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


AMENITY_RESEARCH_SCHEMA = {
    "name": "address_amenity_research",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "address": {"type": "string"},
            "retail": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "nearest_major_retail_name": {"type": "string"},
                    "nearest_major_retail_km": {"type": ["number", "null"]},
                    "major_store_count": {"type": "integer"},
                    "has_pharmacy": {"type": "boolean"},
                    "has_backup_retail": {"type": "boolean"},
                    "evidence": {"type": "string"},
                },
                "required": [
                    "nearest_major_retail_name",
                    "nearest_major_retail_km",
                    "major_store_count",
                    "has_pharmacy",
                    "has_backup_retail",
                    "evidence",
                ],
            },
            "transport": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "nearest_station_name": {"type": "string"},
                    "nearest_station_km": {"type": ["number", "null"]},
                    "has_bus_support": {"type": "boolean"},
                    "has_multiple_station_options": {"type": "boolean"},
                    "evidence": {"type": "string"},
                },
                "required": [
                    "nearest_station_name",
                    "nearest_station_km",
                    "has_bus_support",
                    "has_multiple_station_options",
                    "evidence",
                ],
            },
            "schools": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "nearest_primary_school_name": {"type": "string"},
                    "nearest_primary_school_km": {"type": ["number", "null"]},
                    "nearest_secondary_school_name": {"type": "string"},
                    "nearest_secondary_school_km": {"type": ["number", "null"]},
                    "primary_school_count_within_5km": {"type": "integer"},
                    "secondary_school_count_within_7km": {"type": "integer"},
                    "evidence": {"type": "string"},
                },
                "required": [
                    "nearest_primary_school_name",
                    "nearest_primary_school_km",
                    "nearest_secondary_school_name",
                    "nearest_secondary_school_km",
                    "primary_school_count_within_5km",
                    "secondary_school_count_within_7km",
                    "evidence",
                ],
            },
            "childcare": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "nearest_childcare_name": {"type": "string"},
                    "nearest_childcare_km": {"type": ["number", "null"]},
                    "childcare_count_within_3km": {"type": "integer"},
                    "has_on_estate_childcare": {"type": "boolean"},
                    "evidence": {"type": "string"},
                },
                "required": [
                    "nearest_childcare_name",
                    "nearest_childcare_km",
                    "childcare_count_within_3km",
                    "has_on_estate_childcare",
                    "evidence",
                ],
            },
            "medical": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "nearest_gp_name": {"type": "string"},
                    "nearest_gp_km": {"type": ["number", "null"]},
                    "nearest_hospital_name": {"type": "string"},
                    "nearest_hospital_km": {"type": ["number", "null"]},
                    "medical_services_count_within_4km": {"type": "integer"},
                    "has_pharmacy": {"type": "boolean"},
                    "has_urgent_care": {"type": "boolean"},
                    "evidence": {"type": "string"},
                },
                "required": [
                    "nearest_gp_name",
                    "nearest_gp_km",
                    "nearest_hospital_name",
                    "nearest_hospital_km",
                    "medical_services_count_within_4km",
                    "has_pharmacy",
                    "has_urgent_care",
                    "evidence",
                ],
            },
            "parks": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "nearest_park_name": {"type": "string"},
                    "nearest_park_km": {"type": ["number", "null"]},
                    "has_playground": {"type": "boolean"},
                    "park_count_within_3km": {"type": "integer"},
                    "has_walking_tracks": {"type": "boolean"},
                    "evidence": {"type": "string"},
                },
                "required": [
                    "nearest_park_name",
                    "nearest_park_km",
                    "has_playground",
                    "park_count_within_3km",
                    "has_walking_tracks",
                    "evidence",
                ],
            },
            "sports": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "nearest_sports_facility_name": {"type": "string"},
                    "nearest_sports_facility_km": {"type": ["number", "null"]},
                    "sports_facility_count_within_5km": {"type": "integer"},
                    "sports_facility_types": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "evidence": {"type": "string"},
                },
                "required": [
                    "nearest_sports_facility_name",
                    "nearest_sports_facility_km",
                    "sports_facility_count_within_5km",
                    "sports_facility_types",
                    "evidence",
                ],
            },
            "freeway": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "nearest_freeway_name": {"type": "string"},
                    "nearest_freeway_entry_km": {"type": ["number", "null"]},
                    "evidence": {"type": "string"},
                },
                "required": [
                    "nearest_freeway_name",
                    "nearest_freeway_entry_km",
                    "evidence",
                ],
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
                    "evidence": {"type": "string"},
                },
                "required": [
                    "confirmed_future_projects_count",
                    "has_major_confirmed_project",
                    "future_development_certainty",
                    "evidence",
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
                    "evidence": {"type": "string"},
                },
                "required": ["crime_level", "crime_trend", "evidence"],
            },
        },
        "required": [
            "address",
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


def research_amenities_from_address(address):
    prompt = f"""
You are an Australian suburb amenity research assistant.

TASK:
Research this address and return structured amenity data for scoring.

ADDRESS:
{address}

You must find practical amenity information for these 10 categories:
1. Retail Access
2. Transport Access
3. Schools
4. Childcare
5. Medical
6. Parks
7. Sports Facilities
8. Freeway Access
9. Future Development
10. Crime Safety

RESEARCH RULES:
- Focus on the exact address first, then nearby suburb/postcode.
- Use Australian context.
- Prefer official or reliable public sources.
- Do not invent exact distances.
- If distance cannot be confidently verified, return null.
- Distances must be in kilometres.
- For counts, count only practical nearby options.
- If a count cannot be verified, use 0.
- If evidence is weak, say "Not verified" in the evidence field.
- Keep evidence short.
- Do not calculate final scores.
- Return only structured data matching the schema.

CATEGORY RULES:
Retail:
- Look for nearest Coles, Woolworths, Aldi, shopping centre, pharmacy, and backup retail.
- major_store_count means count of major practical retail options nearby.

Transport:
- Look for nearest train station, V/Line/Metro access, and bus support.

Schools:
- Find nearest primary school and nearest secondary school.
- Count primary schools within about 5 km.
- Count secondary schools within about 7 km.

Childcare:
- Find nearest childcare or early learning centre.
- Count childcare centres within about 3 km.

Medical:
- Find nearest GP clinic and nearest hospital.
- Check pharmacy and urgent care if available.

Parks:
- Find nearest park/open space.
- Check playgrounds, trails, reserves, walking tracks.

Sports:
- Find nearest sports reserve/facility.
- Mention facility types like oval, tennis, cricket, football, recreation centre.

Freeway:
- Find nearest practical freeway or major motorway entry.
- Include freeway name.

Future development:
- Look for council/state/developer confirmed infrastructure:
  schools, town centres, roads, transport, community centres, parks.
- Only count confirmed or clearly supported projects.

Crime:
- Use official crime statistics where possible.
- Compare relative safety conservatively.
"""

    response = client.responses.create(
        model="gpt-5.5",
        tools=[{"type": "web_search_preview"}],
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": AMENITY_RESEARCH_SCHEMA["name"],
                "schema": AMENITY_RESEARCH_SCHEMA["schema"],
                "strict": True,
            }
        },
    )

    return json.loads(response.output_text)
