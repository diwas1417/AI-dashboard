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
