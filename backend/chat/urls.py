from django.urls import path
from .views import ChatSessionListCreateView, ChatMessageListView

urlpatterns = [
    path("sessions/", ChatSessionListCreateView.as_view(), name="chat-sessions"),
    path(
        "sessions/<int:session_id>/messages/",
        ChatMessageListView.as_view(),
        name="chat-messages",
    ),
]
