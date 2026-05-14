import json
import re

import pdfplumber
from django.conf import settings
from openai import OpenAI

MARKET_TREND_PROMPT = """
You are a professional Australian property market data extraction assistant.

I will provide text extracted from a CMA / RPP / CoreLogic / Cotality property report PDF.

IMPORTANT RULES:
- Use only the provided PDF text.
- Do not search the web.
- Do not use external sources.
- Do not guess, estimate, interpolate, or invent missing values.
- Use Australian English.
- If any value is unclear or not visible, write exactly: Not verified.

TASK:
Find the section titled "Long Term Market Trends".

Extract the table from that section only.

Use these exact columns:
Period
Properties Sold
Median Value
Growth
Days on Market
Listings
Asking Rent

Split the extracted rows into:
1. pre_covid_table: include only 2010 to 2019
2. post_covid_table: include only 2020 to latest available year

Also identify:
- suburb_or_postcode
- report_type, for example Houses Only

FORMATTING:
- Median Value must be formatted like $980,015
- Asking Rent must be formatted like $565
- Growth should keep the percentage and arrow if visible, for example 6.8% ▲ or -3.9% ▼
- Do not change numbers from the PDF text.

Return only valid JSON in this exact structure:

{
  "suburb_or_postcode": "",
  "report_type": "",
  "pre_covid_table": [
    {
      "Period": "",
      "Properties Sold": "",
      "Median Value": "",
      "Growth": "",
      "Days on Market": "",
      "Listings": "",
      "Asking Rent": ""
    }
  ],
  "post_covid_table": [
    {
      "Period": "",
      "Properties Sold": "",
      "Median Value": "",
      "Growth": "",
      "Days on Market": "",
      "Listings": "",
      "Asking Rent": ""
    }
  ]
}

No markdown.
No explanation.
JSON only.
"""


def extract_pdf_text(pdf_file):
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


def call_openai_for_market_trends(extracted_text):
    api_key = getattr(settings, "OPENAI_API_KEY", None)

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is missing. Add it to backend/.env and settings.py."
        )

    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=MARKET_TREND_PROMPT,
        input=f"PDF TEXT:\n{extracted_text}",
        temperature=0,
    )

    return clean_json_response(response.output_text)
