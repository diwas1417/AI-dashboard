import json
import re

import pdfplumber
from django.conf import settings
from openai import OpenAI

SUBURB_STATS_PIE_PROMPT = """
You are a professional Australian suburb statistics data extraction assistant.

I will provide text extracted from a Suburb Statistics Report PDF.

IMPORTANT RULES:
- Use only the provided PDF text.
- Do not search the web.
- Do not use external sources.
- Do not guess, estimate, interpolate, round, rebalance, or modify values.
- Use the exact local suburb percentage values from the PDF.
- Do not use council, comparison, state, national, or benchmark values.
- If any value is unclear or not visible, write exactly: Not verified.

TASK:
Find and extract data for these sections only:

1. Household Structure
2. Education By Qualification
3. Employment By Occupation

For each section:
- Extract all local suburb categories shown in the table.
- Extract exact local suburb percentage values.
- Do not include range-based sections such as Population Age or Household Income.
- Do not include Household Occupancy unless specifically requested.
- Do not add interpretation or commentary.

TOTAL RULE:
- Calculate the total of extracted percentages for each section.
- The total can be any value.
- Do not require the total to equal 100.
- Do not stop if the total is below 99.5 or above 100.5.
- Do not adjust, rebalance, round, or force values to 100.
- Always set can_create_chart to true if there is at least one valid category and percentage.

Return only valid JSON in this exact structure:

{
  "suburb_or_postcode": "",
  "household_structure": {
    "total": 0,
    "can_create_chart": true,
    "items": [
      {
        "category": "",
        "percentage": 0
      }
    ]
  },
  "education_by_qualification": {
    "total": 0,
    "can_create_chart": true,
    "items": [
      {
        "category": "",
        "percentage": 0
      }
    ]
  },
  "employment_by_occupation": {
    "total": 0,
    "can_create_chart": true,
    "items": [
      {
        "category": "",
        "percentage": 0
      }
    ]
  }
}

No markdown.
No explanation.
JSON only.
"""


def extract_pdf_text_for_pie(pdf_file):
    full_text = []

    with pdfplumber.open(pdf_file) as pdf:
        for index, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                full_text.append(f"\n--- PAGE {index + 1} ---\n{text}")

    return "\n".join(full_text)


def clean_json_response(raw_text):
    raw_text = raw_text.strip()
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not match:
        raise ValueError("OpenAI response did not contain valid JSON.")

    return json.loads(match.group())


def call_openai_for_suburb_stats_pie(extracted_text):
    api_key = getattr(settings, "OPENAI_API_KEY", None)

    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing. Add it to backend/.env.")

    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=SUBURB_STATS_PIE_PROMPT,
        input=f"PDF TEXT:\n{extracted_text}",
        temperature=0,
    )

    return clean_json_response(response.output_text)
