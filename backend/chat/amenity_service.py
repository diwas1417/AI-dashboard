from .amenity_mock_data import get_mock_amenity_data
from .amenity_score_rules import (
    get_total_interpretation,
    score_childcare,
    score_crime_safety,
    score_freeway_access,
    score_future_development,
    score_medical,
    score_parks,
    score_retail_access,
    score_schools,
    score_sports_facilities,
    score_transport_access,
)
from .amenity_heatmap import generate_amenity_heatmap
from .openai_amenity_extractor import extract_amenity_inputs_with_openai
from .openai_amenity_researcher import research_amenities_from_address


def build_category_result(category_name, score_reason_tuple):
    score, reason = score_reason_tuple
    return {
        "category": category_name,
        "score": score,
        "reason": reason,
    }


def analyse_address_amenities(
    address, custom_inputs=None, raw_research_text=None, use_openai_research=False
):
    """
    Main service function for amenity scoring.

    Priority:
    1. If custom_inputs is provided, use it directly.
    2. If use_openai_research is true, OpenAI researches from address.
    3. If raw_research_text is provided, OpenAI converts notes to JSON.
    4. Otherwise use mock data.
    """

    if custom_inputs:
        data = custom_inputs
        data["address"] = address
    elif use_openai_research:
        data = research_amenities_from_address(address)
        data["address"] = address
    elif raw_research_text:
        data = extract_amenity_inputs_with_openai(
            address=address,
            raw_research_text=raw_research_text,
        )
        data["address"] = address
    else:
        data = get_mock_amenity_data(address)

    category_results = [
        build_category_result(
            "Retail Access", score_retail_access(data.get("retail", {}))
        ),
        build_category_result(
            "Transport Access", score_transport_access(data.get("transport", {}))
        ),
        build_category_result("Schools", score_schools(data.get("schools", {}))),
        build_category_result("Childcare", score_childcare(data.get("childcare", {}))),
        build_category_result("Medical", score_medical(data.get("medical", {}))),
        build_category_result("Parks", score_parks(data.get("parks", {}))),
        build_category_result(
            "Sports Facilities", score_sports_facilities(data.get("sports", {}))
        ),
        build_category_result(
            "Freeway Access", score_freeway_access(data.get("freeway", {}))
        ),
        build_category_result(
            "Future Development",
            score_future_development(data.get("future_development", {})),
        ),
        build_category_result(
            "Crime Safety", score_crime_safety(data.get("crime", {}))
        ),
    ]

    total_score = sum(item["score"] for item in category_results)
    interpretation = get_total_interpretation(total_score)

    heatmap_url = generate_amenity_heatmap(
        address=address,
        category_results=category_results,
        total_score=total_score,
        interpretation=interpretation,
    )

    return {
        "status": "success",
        "address": address,
        "total_score": total_score,
        "score_out_of": 100,
        "interpretation": interpretation,
        "category_results": category_results,
        "heatmap_url": heatmap_url,
        "raw_inputs_used": data,
        "note": "This version uses mock/manual input data. Live Google/official-source data collection will be added later.",
    }
