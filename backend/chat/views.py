import logging
import os
import requests

from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer

from .services import calculate_distance_between_addresses, ask_gemini
from .pdf_market_service import extract_pdf_text, call_openai_for_market_trends
from .market_chart import generate_market_trend_chart
from .extracted_json import save_extracted_json
from django.conf import settings
from .pie_chart_service import (
    extract_pdf_text_for_pie,
    call_openai_for_suburb_stats_pie,
)
from .pie_chart_generator import generate_all_pie_charts

from .pdf_market_service import extract_pdf_text, call_openai_for_market_trends
from .market_chart import generate_market_trend_chart
from .extracted_json import save_extracted_json

logger = logging.getLogger("chat")


def get_temp_user():
    user, created = User.objects.get_or_create(username="testuser")

    if created:
        logger.info("Temporary user created | username=testuser")

    return user


class ChatSessionListCreateView(APIView):
    def get(self, request):
        user = get_temp_user()

        sessions = ChatSession.objects.filter(user=user, is_deleted=False).order_by(
            "-updated_at"
        )

        logger.info(
            f"Chat sessions fetched | user={user.username} | count={sessions.count()}"
        )

        serializer = ChatSessionSerializer(sessions, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = get_temp_user()
        title = request.data.get("title", "New Chat").strip()

        if not title:
            title = "New Chat"

        session = ChatSession.objects.create(user=user, title=title)

        logger.info(
            f"Chat session created | user={user.username} | session_id={session.id} | title={session.title}"
        )

        serializer = ChatSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ChatMessageListView(APIView):
    def get(self, request, session_id):
        user = get_temp_user()

        try:
            session = ChatSession.objects.get(
                id=session_id, user=user, is_deleted=False
            )
        except ChatSession.DoesNotExist:
            logger.error(
                f"Message fetch failed | session not found | session_id={session_id}"
            )
            return Response(
                {"error": "Chat session not found"}, status=status.HTTP_404_NOT_FOUND
            )

        messages = ChatMessage.objects.filter(
            session=session, is_deleted=False
        ).order_by("created_at")

        logger.info(
            f"Messages fetched | session_id={session_id} | count={messages.count()}"
        )

        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, session_id):
        user = get_temp_user()

        try:
            session = ChatSession.objects.get(
                id=session_id, user=user, is_deleted=False
            )
        except ChatSession.DoesNotExist:
            logger.error(
                f"Message save failed | session not found | session_id={session_id}"
            )
            return Response(
                {"error": "Chat session not found"}, status=status.HTTP_404_NOT_FOUND
            )

        content = request.data.get("content", "").strip()

        if not content:
            logger.error(
                f"Message save failed | empty content | session_id={session_id}"
            )
            return Response(
                {"error": "Message content is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_message = ChatMessage.objects.create(
            session=session, role="user", content=content
        )

        logger.info(
            f"User message saved | session_id={session_id} | message_id={user_message.id}"
        )

        ai_reply = None
        lower_content = content.lower()

        if "distance between" in lower_content and " and " in lower_content:
            try:
                address_part = (
                    content.lower().replace("distance between", "", 1).strip()
                )
                address_one, address_two = address_part.split(" and ", 1)

                result = calculate_distance_between_addresses(
                    address_one.strip(), address_two.strip()
                )

                ai_reply = result["message"]

                logger.info(
                    f"Distance calculated | session_id={session_id} | success={result['success']}"
                )

            except Exception as e:
                logger.error(
                    f"Distance calculation failed | session_id={session_id} | error={str(e)}"
                )
                ai_reply = (
                    "Sorry, I could not calculate the distance between those addresses."
                )

        if ai_reply is None:
            ai_reply = ask_gemini(content)

        ai_message = ChatMessage.objects.create(
            session=session, role="assistant", content=ai_reply
        )

        logger.info(
            f"AI message saved | session_id={session_id} | message_id={ai_message.id}"
        )

        return Response(
            {
                "user_message": ChatMessageSerializer(user_message).data,
                "ai_message": ChatMessageSerializer(ai_message).data,
            },
            status=status.HTTP_201_CREATED,
        )


class MarketTrendPDFAnalysisView(APIView):
    def post(self, request):
        pdf_file = request.FILES.get("pdf")
        print("diwas")
        if not pdf_file:
            return Response(
                {"status": "error", "message": "PDF file is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            extracted_text = extract_pdf_text(pdf_file)

            if not extracted_text.strip():
                return Response(
                    {
                        "status": "error",
                        "message": "No readable text could be extracted from this PDF.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            structured_data = call_openai_for_market_trends(extracted_text)

            json_filename, json_filepath = save_extracted_json(structured_data)

            chart_url, growth_summary = generate_market_trend_chart(structured_data)

            full_chart_url = (
                request.build_absolute_uri(chart_url) if chart_url else None
            )

            json_url = request.build_absolute_uri(
                f"{settings.MEDIA_URL}extracted_json/{json_filename}"
            )

            return Response(
                {
                    "status": "success",
                    "extracted_data": structured_data,
                    "json_file": json_filename,
                    "json_url": json_url,
                    "chart_url": full_chart_url,
                    "growth_summary": growth_summary,
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
