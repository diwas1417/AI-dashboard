from django.urls import path

from .views import (
    ChatSessionListCreateView,
    ChatMessageListView,
    MarketTrendPDFAnalysisView,
)

from .pie_chart_views import (
    SuburbStatsPieChartFromJSONView,
    SuburbStatsPieChartAnalysisView,
    SuburbStatsEditPDFFromSampleJSONView,
)
from .amenity_views import AmenityScoreAnalysisView

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
    path(
        "suburb-stats/pie-charts/",
        SuburbStatsPieChartAnalysisView.as_view(),
        name="suburb-stats-pie-charts",
    ),
    path(
        "suburb-stats/pie-charts-from-json/",
        SuburbStatsPieChartFromJSONView.as_view(),
        name="suburb-stats-pie-charts-from-json",
    ),
    path(
        "suburb-stats/edit-pdf-from-sample-json/",
        SuburbStatsEditPDFFromSampleJSONView.as_view(),
        name="suburb-stats-edit-pdf-from-sample-json",
    ),
    path(
        "amenity-score/",
        AmenityScoreAnalysisView.as_view(),
        name="amenity-score",
    ),
]
