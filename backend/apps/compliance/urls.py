from django.urls import path
from . import views

urlpatterns = [
    path('alerts/', views.ComplianceAlertListView.as_view(), name='compliance-alerts'),
]