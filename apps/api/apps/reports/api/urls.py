from django.urls import path
from .views import DashboardSummaryView, ReportExportView

urlpatterns = [
    path('reports/dashboard', DashboardSummaryView.as_view(), name='reports-dashboard'),
    path('reports/summary/', DashboardSummaryView.as_view(), name='reports-summary'),
    path('reports/export/', ReportExportView.as_view(), name='report-export'),
]
