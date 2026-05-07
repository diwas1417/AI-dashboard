from rest_framework import serializers
from .models import ChatMessage, ChatSession


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "session",
            "role",
            "content",
            "is_deleted",
            "deleted_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "is_deleted", "deleted_at"]


class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = [
            "id",
            "user",
            "title",
            "created_at",
            "updated_at",
            "is_deleted",
            "deleted_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "is_deleted",
            "deleted_at",
        ]
