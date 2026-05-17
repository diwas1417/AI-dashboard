import json
import os

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .pie_chart_generator import generate_all_pie_charts
from .pie_chart_service import (
    extract_pdf_text_for_pie,
    call_openai_for_suburb_stats_pie,
)
from .pdf_pie_editor import edit_suburb_statistics_pdf_with_pie_charts


class SuburbStatsPieChartFromJSONView(APIView):
    """
    Test endpoint:
    JSON data -> pie chart images

    This does not use OpenAI API.
    """

    def post(self, request):
        try:
            data = request.data

            charts = generate_all_pie_charts(data)

            full_chart_urls = {}
            for key, value in charts.items():
                full_chart_urls[key] = (
                    request.build_absolute_uri(value) if value else None
                )

            return Response(
                {
                    "status": "success",
                    "extracted_data": data,
                    "charts": full_chart_urls,
                    "total_checks": {
                        "household_structure_total": data.get(
                            "household_structure", {}
                        ).get("total"),
                        "education_by_qualification_total": data.get(
                            "education_by_qualification", {}
                        ).get("total"),
                        "employment_by_occupation_total": data.get(
                            "employment_by_occupation", {}
                        ).get("total"),
                    },
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SuburbStatsPieChartAnalysisView(APIView):
    """
    Full endpoint:
    PDF upload -> OpenAI extraction -> pie chart images
    """

    def post(self, request):
        pdf_file = request.FILES.get("pdf")

        if not pdf_file:
            return Response(
                {"status": "error", "message": "PDF file is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            extracted_text = extract_pdf_text_for_pie(pdf_file)

            if not extracted_text.strip():
                return Response(
                    {
                        "status": "error",
                        "message": "No readable text could be extracted from this PDF.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            structured_data = call_openai_for_suburb_stats_pie(extracted_text)

            charts = generate_all_pie_charts(structured_data)

            edited_pdf_url, edited_pdf_path = (
                edit_suburb_statistics_pdf_with_pie_charts(
                    pdf_file,
                    charts,
                )
            )

            full_chart_urls = {}
            for key, value in charts.items():
                full_chart_urls[key] = (
                    request.build_absolute_uri(value) if value else None
                )

            return Response(
                {
                    "status": "success",
                    "extracted_data": structured_data,
                    "charts": full_chart_urls,
                    "edited_pdf_url": request.build_absolute_uri(edited_pdf_url),
                    "total_checks": {
                        "household_structure_total": structured_data.get(
                            "household_structure", {}
                        ).get("total"),
                        "education_by_qualification_total": structured_data.get(
                            "education_by_qualification", {}
                        ).get("total"),
                        "employment_by_occupation_total": structured_data.get(
                            "employment_by_occupation", {}
                        ).get("total"),
                    },
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SuburbStatsEditPDFFromSampleJSONView(APIView):
    """
    Testing endpoint:
    Upload PDF -> use sample_pie_data.json -> generate charts -> edit PDF

    This does NOT use OpenAI API.
    """

    def post(self, request):
        pdf_file = request.FILES.get("pdf")

        if not pdf_file:
            return Response(
                {"status": "error", "message": "PDF file is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            sample_json_path = os.path.join(settings.BASE_DIR, "sample_pie_data.json")

            if not os.path.exists(sample_json_path):
                return Response(
                    {
                        "status": "error",
                        "message": "sample_pie_data.json file not found in backend folder.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with open(sample_json_path, "r", encoding="utf-8") as file:
                sample_data = json.load(file)

            charts = generate_all_pie_charts(sample_data)

            edited_pdf_url, edited_pdf_path = (
                edit_suburb_statistics_pdf_with_pie_charts(
                    pdf_file,
                    charts,
                )
            )

            full_chart_urls = {}
            for key, value in charts.items():
                full_chart_urls[key] = (
                    request.build_absolute_uri(value) if value else None
                )

            return Response(
                {
                    "status": "success",
                    "message": "PDF edited successfully using sample JSON data.",
                    "sample_data_used": sample_data,
                    "charts": full_chart_urls,
                    "edited_pdf_url": request.build_absolute_uri(edited_pdf_url),
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
