from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .amenity_service import analyse_address_amenities


class AmenityScoreAnalysisView(APIView):
    def post(self, request):
        address = request.data.get("address")
        inputs = request.data.get("inputs")
        raw_research_text = request.data.get("raw_research_text")
        use_openai_research = request.data.get("use_openai_research", False)

        if not address:
            return Response(
                {
                    "status": "error",
                    "message": "Address is required.",
                    "example": {
                        "address": "25 Example Street, Sunbury VIC",
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = analyse_address_amenities(
                address=address,
                custom_inputs=inputs,
                raw_research_text=raw_research_text,
                use_openai_research=use_openai_research,
            )
            return Response(result, status=status.HTTP_200_OK)

        except Exception as error:
            return Response(
                {
                    "status": "error",
                    "message": "Amenity scoring failed.",
                    "details": str(error),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
