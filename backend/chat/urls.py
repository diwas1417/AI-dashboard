from django.urls import path
from .views import (
    ChatSessionListCreateView,
    ChatMessageListView,
    MarketTrendPDFAnalysisView,
)

urlpatterns = [
    path("sessions/", ChatSessionListCreateView.as_view(), name="chat-sessions"),
    path(
        "sessions/<int:session_id>/messages/",
        ChatMessageListView.as_view(),
        name="chat-messages",
    ),
    path(
        "market-trends/analyse/",
        MarketTrendPDFAnalysisView.as_view(),
        name="market-trends-analyse",
    ),
]
